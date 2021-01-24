import React, { useState } from "react";
import { Redirect } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Modal, Menu, Divider, Typography } from "antd";
import { FileAddOutlined, DeleteOutlined } from "@ant-design/icons";
import ReactMarkdown from "react-markdown";
import PostSubscriptionResult from "./PostSubscriptionResult";
import EmailSubscriptionForm from "./EmailSubscriptionForm";
import EmailUnsubscriptionForm from "./EmailUnsubscriptionForm";
import useSubscriptionFormControl from "./useSubscriptionFormControl";

export default function EmailSubscription() {
    const [subsOp, setSubsOp] = useState("subscription"); // subscriptionOp from a fake "tab"
    const { t } = useTranslation();
    const [{ form, formState }, pageInfo, postSubscription] = useSubscriptionFormControl(subsOp);
    const { inEmailPage, subscriptionOp, step, redirect } = pageInfo;

    if (redirect) {
        return <Redirect to="/visa" />;
    }

    const EmailForm = () =>
        subscriptionOp === "subscription" ? (
            <EmailSubscriptionForm
                formControl={{ form, formState }}
                pageInfo={pageInfo}
                cookieOption="both"
                onFinish={fieldValues => postSubscription(fieldValues)}
            />
        ) : (
            <EmailUnsubscriptionForm
                formControl={{ form, formState }}
                pageInfo={pageInfo}
                onFinish={fieldValues => postSubscription(fieldValues)}
            />
        );

    const PostResult = () => (
        <PostSubscriptionResult success={formState.postSuccessful} step={step} inEmailPage={inEmailPage} />
    );

    return (
        <>
            <ReactMarkdown>{t("emailForm.description")}</ReactMarkdown>
            {!inEmailPage && (
                <>
                    <Menu
                        onClick={() => setSubsOp(subsOp === "subscription" ? "unsubscription" : "subscription")}
                        selectedKeys={[subsOp]}
                        mode="horizontal"
                    >
                        <Menu.Item key="subscription" icon={<FileAddOutlined />}>
                            <Typography.Text strong>{t("emailForm.tab.subscription")}</Typography.Text>
                        </Menu.Item>
                        <Menu.Item key="unsubscription" icon={<DeleteOutlined />}>
                            <Typography.Text strong>{t("emailForm.tab.unsubscription")}</Typography.Text>
                        </Menu.Item>
                    </Menu>
                    <Divider />
                </>
            )}
            {!inEmailPage && formState.posting ? <PostResult /> : <EmailForm />}
            {inEmailPage && (
                <Modal visible={formState.modalVisible} footer={null}>
                    <PostResult />
                </Modal>
            )}
        </>
    );
}
