import { useEffect, useMemo, useReducer, useCallback } from "react";
import { Form } from "antd";
import { useLocation } from "react-router-dom";
import { useSelector } from "react-redux";
import { postEmailSubscription } from "../services";
import { isoStringToMoment, momentToISOString, zip } from "../utils/misc";
import { deleteCookie, getCookie, setCookie } from "../utils/cookie";

/**
 * Construct request body from subcription form
 *
 * @param {Object} fieldValues Form field values object
 * @param {string} fieldValues.email Email address
 * @param {Object[]} fieldValues.subscription Subscriptions of users
 * @param {string} fieldValues.subscription.visaType Visa type of single subscription
 * @param {string} fieldValues.subscription.embassyCode Embassy code of single subscription
 * @param {moment} [fieldValues.subscription.till] Subscription end date of single subscription
 *
 * @returns {Object} request body
 */
const reqBodyFromForm = ({ email, subscription }) => ({
    email,
    subscription: subscription.map(subs => ({
        visa_type: subs.visaType,
        code: subs.embassyCode,
        till: subs.till ? momentToISOString(subs.till) : null,
    })),
});
/**
 * Construct request body from URLSearchParam
 *
 * @param {URLSearchParams} param The passed url search param.
 * @returns {Object} request body
 */
const reqBodyFromParam = param => ({
    email: param.get("email"),
    subscription: zip(
        param.getAll("visa_type"),
        param.getAll("code"),
        param.getAll("till"),
    ).map(([vt, code, till]) => ({ visa_type: vt, code, till })),
});

const { useForm } = Form;

const formStateActions = {
    SET_MODAL_VISIBLE: "SET_MODAL_VISIBLE",
    SET_POSTING_SUBS: "SET_POSTING_SUBSCRIPTION",
    SET_POSTING_RESULT: "SET_POSTING_RESULT",
    START_POSTING: "START_POSTING",
    END_POSTING: "END_POSTING",
    RESET: "RESET",
};
const initialFormState = { modalVisible: false, postingSubscription: false, postSuccessful: null };
const formStateReducer = (state, action) => {
    switch (action.type) {
        case formStateActions.SET_MODAL_VISIBLE:
            return { ...state, modalVisible: action.payload.visible };
        case formStateActions.SET_POSTING_SUBS:
            return { ...state, postingSubscription: action.payload.posting };
        case formStateActions.SET_POSTING_RESULT:
            return { ...state, postSuccessful: action.payload.result };
        case formStateActions.START_POSTING:
            return { ...state, modalVisible: true, postingSubscription: true };
        case formStateActions.END_POSTING:
        case formStateActions.RESET:
            return initialFormState;
        default:
            return state;
    }
};

/**
 * Custom hook to return encapsulated form control for rendering the subscription form.
 *
 * @param {string} [embassyCode] The embassy code.
 * @returns {[FormInstance, {Object, Function, Object}, string, URLSearchParams, Function]} Form controls including a form instance and a reducer for controling the modal
 */
export default function useSubscriptionFormControl(embassyCode) {
    const [formState, dispatchFormAction] = useReducer(formStateReducer, initialFormState);
    const visaType = useSelector(state => state.visastatusTab);
    const [form] = useForm();
    const location = useLocation();
    const param = useMemo(() => new URLSearchParams(location.search), [location]);
    const inSubscriptionPage = useMemo(() => location.pathname === "/visa/email/subscription", [location]);

    // Set initial form fields values, use this instead of static `initialValues` prop
    useEffect(() => {
        if (!param.toString()) {
            const email = getCookie("email", { email: "" });
            const { subscription } = getCookie("subscription", { subscription: [] });
            form.setFieldsValue(
                inSubscriptionPage
                    ? {
                          ...email,
                          subscription: subscription.map(({ till, ...rest }) => ({
                              ...rest,
                              till: till ? isoStringToMoment(till) : null,
                          })),
                      }
                    : { ...email, subscription: [{ visaType, embassyCode }] },
            );
        }

        // clean up the cookie when unmount form from page.
        return () => {
            if (inSubscriptionPage) {
                setCookie("subscription", {
                    subscription: getCookie("subscription", { subscription: [] }).subscription.filter(
                        subs => subs.embassyCode,
                    ),
                });
            }
        };
    }, [form, param, visaType, inSubscriptionPage, embassyCode]);

    // Reset form values everytime modal in OverviewContent is closed
    // Seperate from previous useEffect for readability.
    useEffect(() => {
        if (embassyCode && !formState.modalVisible) {
            const email = getCookie("email", { email: "" });
            form.setFieldsValue({ ...email, subscription: [{ visaType, embassyCode }] });
        }
    }, [form, formState.modalVisible, visaType, embassyCode]);

    const postSubscription = useCallback(
        async reqBodyMaterial => {
            const requestBody =
                reqBodyMaterial instanceof URLSearchParams
                    ? reqBodyFromParam(reqBodyMaterial)
                    : reqBodyFromForm(reqBodyMaterial);
            const step = reqBodyMaterial instanceof URLSearchParams ? "subscribed" : "confirming";

            try {
                dispatchFormAction({ type: formStateActions.START_POSTING });

                const postSuccess = await postEmailSubscription(step, requestBody);

                dispatchFormAction({ type: formStateActions.SET_POSTING_RESULT, payload: { result: postSuccess } });
                const timeOut = setTimeout(() => {
                    dispatchFormAction({ type: formStateActions.END_POSTING });
                    clearTimeout(timeOut);
                }, 3000);

                if (step === "subscribed" && postSuccess) {
                    deleteCookie("subscription");
                }
            } catch (error) {
                console.error(`In hook postSubscription: ${error}`);
                dispatchFormAction({ type: formStateActions.SET_POSTING_RESULT, payload: { result: false } });
                const timeOut = setTimeout(() => {
                    dispatchFormAction({ type: formStateActions.END_POSTING });
                    clearTimeout(timeOut);
                }, 3000);
            }
        },
        [dispatchFormAction],
    );

    return [
        { form, formState, dispatchFormAction, formStateActions },
        { visaType, inSubscriptionPage },
        postSubscription,
        param,
    ];
}
