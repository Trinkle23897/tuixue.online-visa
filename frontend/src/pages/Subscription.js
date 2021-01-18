import React from "react";
import { useTranslation } from "react-i18next";
import { Layout, Typography, Row, Col } from "antd";
import { TuixueHeader, EmailSubscription } from "../components";
import "./VisaStatus.less";

const { Content } = Layout;
const { Title } = Typography;

export default function Subscription() {
    const [t] = useTranslation();

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
                        <EmailSubscription />
                    </Col>
                </Row>
            </Content>
        </Layout>
    );
}
