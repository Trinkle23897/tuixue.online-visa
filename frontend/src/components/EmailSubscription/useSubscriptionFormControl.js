import { useState, useEffect, useMemo, useReducer, useCallback } from "react";
import { Form } from "antd";
import { useLocation, useRouteMatch, useParams } from "react-router-dom";
import { useSelector } from "react-redux";
import { makeFilterSelectorByVisaType } from "../../redux/selectors";
import { postEmailSubscription } from "../../services";
import { isoStringToMoment, momentToISOString, zip } from "../../utils/misc";
import { deleteCookie, getCookie, setCookie } from "../../utils/cookie";

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
const reqBodyFromForm = {
    subscription: ({ email, subscription }) => ({
        email,
        subscription: subscription.map(subs => ({
            visa_type: subs.visaType,
            code: subs.embassyCode,
            till: subs.till ? momentToISOString(subs.till) : null,
        })),
    }),
    unsubscription: ({ email }) => ({ email }),
};

/**
 * Construct request body from URLSearchParam
 *
 * @param {URLSearchParams} param The passed url search param.
 * @returns {Object} request body
 */
const reqBodyFromParam = (param, subscriptionOp) => {
    const email = param.get("email");
    const subscriptionRuleCollector = param
        .getAll("visa_type")
        .reduce((subsObj, visaType) => ({ ...subsObj, [visaType]: {} }), {});

    zip(param.getAll("visa_type"), param.getAll("code"), param.getAll("till")).forEach(([vt, code, till]) => {
        subscriptionRuleCollector[vt][till] = subscriptionRuleCollector[vt][till]
            ? [...subscriptionRuleCollector[vt][till], code]
            : [code];
    });

    return {
        email,
        [subscriptionOp]: Object.entries(subscriptionRuleCollector)
            .map(([vt, tillToCode]) =>
                Object.entries(tillToCode).map(([till, code]) => ({ visa_type: vt, code, till })),
            )
            .flat(),
    };
};

const { useForm } = Form;

const formStateActions = {
    SET_MODAL_VISIBLE: "SET_MODAL_VISIBLE",
    SET_POSTING: "SET_POSTING",
    SET_POSTING_RESULT: "SET_POSTING_RESULT",
    START_POSTING: "START_POSTING",
    END_POSTING: "END_POSTING",
    RESET: "RESET",
};
const initialFormState = { modalVisible: false, posting: false, postSuccessful: null };
const formStateReducer = (state, action) => {
    switch (action.type) {
        case formStateActions.SET_MODAL_VISIBLE:
            return { ...state, modalVisible: action.payload.visible };
        case formStateActions.SET_POSTING:
            return { ...state, posting: action.payload.posting };
        case formStateActions.SET_POSTING_RESULT:
            return { ...state, postSuccessful: action.payload.result };
        case formStateActions.START_POSTING:
            return { ...state, modalVisible: true, posting: true };
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
 * @param {string} parentSubscriptionOp subscriptionOp from parents, one of ["subscription", "unsubscription"]
 * @returns {[FormInstance, {Object, Function, Object}, string, URLSearchParams, Function]} Form controls including a form instance and a reducer for controling the modal
 */
export default function useSubscriptionFormControl(parentSubscriptionOp) {
    const [formState, dispatchFormAction] = useReducer(formStateReducer, initialFormState);
    const [form] = useForm();

    const visaType = useSelector(state => state.visastatusTab);
    const filterSelector = useMemo(() => makeFilterSelectorByVisaType(visaType), [visaType]);
    const visastatusFilter = useSelector(state => filterSelector(state));

    const match = useRouteMatch("/visa/email/:subscriptionOp");
    const inEmailPage = useMemo(() => !!match && match.isExact, [match]);
    const { subscriptionOp: pageSubscriptionOp } = useParams();

    // subscriptionOp from page param ('/visa/email/:subscriptionOp) take higher priority
    const subscriptionOp = useMemo(() => pageSubscriptionOp || parentSubscriptionOp, [
        pageSubscriptionOp,
        parentSubscriptionOp,
    ]);

    const location = useLocation();
    const param = useMemo(() => new URLSearchParams(location.search), [location]);

    // determine the step here.
    const step = useMemo(
        () =>
            inEmailPage
                ? param.toString()
                    ? subscriptionOp === "subscription"
                        ? "subscribed"
                        : "deleted"
                    : "confirming"
                : "confirming",
        [inEmailPage, param, subscriptionOp],
    );

    // Set initial form fields values, use this instead of static `initialValues` prop
    useEffect(() => {
        if (!param.toString()) {
            const email = getCookie("email", { email: "" });
            const { subscription } = getCookie("subscription", {
                subscription: [{ visaType, embassyCode: [...visastatusFilter], till: null }],
            });
            form.setFieldsValue(
                subscriptionOp === "subscription"
                    ? {
                          ...email,
                          subscription: subscription.map(({ till, ...rest }) => ({
                              ...rest,
                              till: till ? isoStringToMoment(till) : null,
                          })),
                      }
                    : email,
            );
        }

        // clean up the cookie when unmount form from page.
        return () => {
            if (inEmailPage && subscriptionOp === "subscription") {
                setCookie("subscription", {
                    subscription: getCookie("subscription", { subscription: [] }).subscription.filter(
                        subs => subs.embassyCode,
                    ),
                });
            }
        };
    }, [form, param, visaType, visastatusFilter, inEmailPage, subscriptionOp]);

    const postSubscription = useCallback(
        async reqBodyMaterial => {
            const requestBody =
                reqBodyMaterial instanceof URLSearchParams
                    ? reqBodyFromParam(reqBodyMaterial, subscriptionOp)
                    : reqBodyFromForm[subscriptionOp](reqBodyMaterial);

            try {
                dispatchFormAction({ type: formStateActions.START_POSTING });

                const postSuccess = await postEmailSubscription(subscriptionOp, step, requestBody);

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
        [dispatchFormAction, subscriptionOp, step],
    );

    // Below hooks are for control in `/visa/email/:subscriptionOp
    const [pageRedirect, setPageRedirect] = useState(false);
    const redirect = useMemo(
        () => inEmailPage && (!["subscription", "unsubscription"].includes(subscriptionOp) || pageRedirect),
        [inEmailPage, subscriptionOp, pageRedirect],
    );

    useEffect(() => {
        if (inEmailPage && param.toString()) {
            postSubscription(param);
        }
    }, [inEmailPage, param, postSubscription]);

    // start redirect count down after second step of 'subscribed'/'deleted'.
    useEffect(() => {
        if (inEmailPage && formState.modalVisible && formState.postSuccessful !== null) {
            const timeOut = setTimeout(() => {
                setPageRedirect(true);
                clearTimeout(timeOut);
            }, 3000);
        }
    }, [inEmailPage, formState]);

    return [
        { form, formState, dispatchFormAction, formStateActions },
        { visaType, inEmailPage, subscriptionOp, step, redirect },
        postSubscription,
    ];
}
