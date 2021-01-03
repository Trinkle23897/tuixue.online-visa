import React, { useState } from "react";
import PropTypes from "prop-types";
import { useSelector } from "react-redux";
import { Button, DatePicker, Form, Input, Row, Col, Select } from "antd";
import { MinusOutlined, PlusOutlined } from "@ant-design/icons";
import { useScreenXS } from "../hooks";
import { momentToISOString } from "../utils/misc";
import { setCookie } from "../utils/cookie";
import EmbassyTreeSelect from "./EmbassyTreeSelect";

const SubscriptionFormItem = ({ field, remove, disabled }) => {
    const [sys, setSys] = useState("all"); // I HATE THIS, NEED TO BE FIXED ASAP
    const visaTypeDetails = useSelector(state => state.metadata.visaTypeDetails);
    const screenXS = useScreenXS();

    return (
        <Row align="middle" justify="space-between">
            <Col xs={{ span: 24 }} md={{ span: 7 }}>
                <Form.Item
                    label="Visa Type"
                    name={[field.name, "visaType"]}
                    fieldKey={[field.fieldKey, "visaType"]}
                    rules={[{ required: true, message: "Visa Type field is required!" }]}
                >
                    <Select
                        options={Object.entries(visaTypeDetails).map(([vt, vtDetail]) => ({
                            label: vtDetail,
                            value: vt,
                        }))}
                        placeholder="Select Visa Type"
                        disabled={disabled}
                    />
                </Form.Item>
            </Col>
            <Col xs={{ span: 24 }} md={{ span: 7 }}>
                <Form.Item
                    label="Embassy"
                    name={[field.name, "embassyCode"]}
                    fieldKey={[field.fieldKey, "embassyCode"]}
                    rules={[{ required: true, message: "Embassy field is required!" }]}
                >
                    <EmbassyTreeSelect
                        sys={sys}
                        setSys={s => setSys(s)}
                        placeholder="Select Embassy"
                        disabled={disabled}
                    />
                </Form.Item>
            </Col>
            <Col xs={{ span: 24 }} md={{ span: 7 }}>
                <Form.Item label="Till" name={[field.name, "till"]} fieldKey={[field.fieldKey, "till"]}>
                    <DatePicker style={{ width: "100%" }} placeholder="Select Till" disabled={disabled} />
                </Form.Item>
            </Col>
            <Col>
                <Button
                    shape={!screenXS && "circle"}
                    block={screenXS}
                    onClick={() => remove(field.name)}
                    style={{ marginBottom: 24 }}
                    disabled={disabled}
                >
                    <MinusOutlined />
                    {screenXS && "Remove Subscription Item"}
                </Button>
            </Col>
        </Row>
    );
};
SubscriptionFormItem.propTypes = {
    field: PropTypes.shape({
        name: PropTypes.number.isRequired,
        key: PropTypes.number.isRequired,
        fieldKey: PropTypes.number.isRequired,
        isListField: PropTypes.bool.isRequired,
    }).isRequired,
    remove: PropTypes.func.isRequired,
    disabled: PropTypes.bool.isRequired,
};

export default function EmailSubscriptionForm({ formControl, pageInfo, cookieOption, onFinish, ...otherFormProps }) {
    const { form, formState } = formControl;
    const { visaType, inSubscriptionPage } = pageInfo;
    // store user input in cookie
    const onValuesChange = (changedValue, allValues) => {
        const setEmailCookie = () => changedValue.email && setCookie("email", { email: allValues.email });
        const setSubsCookie = () =>
            changedValue.subscription &&
            setCookie("subscription", {
                subscription: allValues.subscription.map(({ till, ...rest }) => ({
                    ...rest,
                    till: till ? momentToISOString(till) : null,
                })),
            });

        switch (cookieOption) {
            case "both":
                setEmailCookie();
                setSubsCookie();
                break;
            case "email":
                setEmailCookie();
                break;
            case "subscription":
                setSubsCookie();
                break;
            default:
                break;
        }
    };

    return (
        <Form
            {...otherFormProps}
            name="emailSubscriptionForm"
            form={form}
            labelCol={{ span: 0 }}
            size="large"
            onValuesChange={onValuesChange}
            onFinish={fieldValues => onFinish(fieldValues)}
        >
            <Form.Item
                name="email"
                label="Email"
                rules={[{ type: "email", required: true, message: "Email address is required!" }]}
            >
                <Input placeholder="Email address" disabled={formState.postingSubscription} />
            </Form.Item>

            <Form.List
                name="subscription"
                style={{ width: "100%" }}
                rules={[
                    {
                        validator: async (_, subscription) => {
                            if (!subscription || subscription.length < 1) {
                                return Promise.reject(new Error("You need to subscribe at least 1 Embassy!"));
                            }
                        },
                    },
                ]}
            >
                {(fields, { add, remove }) => (
                    <>
                        {fields.map(field => (
                            <SubscriptionFormItem
                                key={field.name}
                                field={field}
                                remove={fn => remove(fn)}
                                disabled={formState.postingSubscription}
                            />
                        ))}
                        <Form.Item>
                            <Button
                                type="default"
                                onClick={() => add({ visaType })}
                                block
                                icon={<PlusOutlined />}
                                disabled={formState.postingSubscription}
                            >
                                Add Subscription Item
                            </Button>
                        </Form.Item>
                    </>
                )}
            </Form.List>
            {inSubscriptionPage && (
                <Form.Item>
                    <Button type="primary" htmlType="submit" block>
                        Subscribe
                    </Button>
                </Form.Item>
            )}
        </Form>
    );
}
EmailSubscriptionForm.propTypes = {
    formControl: PropTypes.shape({
        form: PropTypes.any.isRequired,
        formState: PropTypes.object.isRequired,
    }).isRequired,
    pageInfo: PropTypes.shape({
        visaType: PropTypes.string.isRequired,
        inSubscriptionPage: PropTypes.bool.isRequired,
    }).isRequired,
    cookieOption: PropTypes.oneOf(["email", "subscription", "both"]).isRequired,
    onFinish: PropTypes.func.isRequired,
};
