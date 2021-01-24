import React from "react";
import PropTypes from "prop-types";
import { useTranslation } from "react-i18next";
import { Form, Button, Input } from "antd";
import { setCookie } from "../../utils/cookie";

export default function EmailUnsubscriptionForm({ formControl, pageInfo, onFinish, ...otherFormProps }) {
    const { t } = useTranslation();
    const { form, formState } = formControl;

    const onValuesChange = (changedValue, allValues) =>
        changedValue.email && setCookie("email", { email: allValues.email });

    return (
        <Form
            {...otherFormProps}
            name="emailUnsubscriptionForm"
            form={form}
            labelCol={{ span: 0 }}
            size="large"
            onValuesChange={onValuesChange}
            onFinish={fieldValues => onFinish(fieldValues)}
        >
            <Form.Item
                name="email"
                label="Email"
                rules={[{ type: "email", required: true, message: t("emailForm.requireEmail") }]}
            >
                <Input placeholder={t("emailForm.emailAddress")} disabled={formState.posting} />
            </Form.Item>
            <Form.Item>
                <Button type="primary" htmlType="submit" block danger>
                    {t("emailForm.unsubscribe")}
                </Button>
            </Form.Item>
        </Form>
    );
}
EmailUnsubscriptionForm.propTypes = {
    formControl: PropTypes.shape({
        form: PropTypes.any.isRequired,
        formState: PropTypes.object.isRequired,
    }).isRequired,
    pageInfo: PropTypes.shape({
        visaType: PropTypes.string.isRequired,
        inEmailPage: PropTypes.bool.isRequired,
        subscriptionOp: PropTypes.oneOf(["subscription", "unsubscription"]),
    }).isRequired,
    onFinish: PropTypes.func.isRequired,
};
