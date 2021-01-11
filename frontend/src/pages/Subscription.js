import React, { useEffect, useState } from "react";
import { Redirect } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Layout, Typography, Modal, Row, Col } from "antd";
import { TuixueHeader, EmailSubscriptionForm } from "../components";
import { useSubscriptionFormControl } from "../hooks";
import "./VisaStatus.less";
import PostSubscriptionResult from "../components/PostSubscriptionResult";

const { Content } = Layout;
const { Title } = Typography;

export default function Subscription() {
    const [t] = useTranslation();
    const [redirect, setRedirect] = useState(false);
    const [{ form, formState }, pageInfo, postSubscription, param] = useSubscriptionFormControl();

    useEffect(() => {
        if (param.toString()) {
            postSubscription(param);
        }
    }, [param, postSubscription]);

    useEffect(() => {
        if (formState.modalVisible && formState.postSuccessful !== null) {
            const timeOut = setTimeout(() => {
                setRedirect(true);
                clearTimeout(timeOut);
            }, 3000);
        }
    }, [formState]);

    return (
        <Layout className="tuixue-page">
            <TuixueHeader />
            <Content className="tuixue-content">
                <Title level={2} style={{ textAlign: "center", margin: "8px", padding: "8px" }}>
                    {t("emailForm.title")}
                </Title>
                <Row>
                    <Col
                        xs={{ span: 22, push: 1 }}
                        sm={{ span: 22, push: 1 }}
                        md={{ span: 20, push: 2 }}
                        lg={{ span: 16, push: 4 }}
                        xl={{ span: 14, push: 5 }}
                    >
                        <EmailSubscriptionForm
                            formControl={{ form, formState }}
                            pageInfo={pageInfo}
                            cookieOption="both"
                            onFinish={fieldValues => postSubscription(fieldValues)}
                        />
                    </Col>
                    <Modal visible={formState.modalVisible} footer={null}>
                        <PostSubscriptionResult
                            success={formState.postSuccessful}
                            step="subscribed"
                            inSubscriptionPage={pageInfo.inSubscriptionPage}
                        />
                    </Modal>
                    {redirect && <Redirect to="/" />}
                </Row>
            </Content>
        </Layout>
    );
}
