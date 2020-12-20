import React from "react";
import { Layout, Typography, Row, Col } from "antd";
import { TuixueHeader, VisaStatusTabs } from "../components";
import "./VisaStatus.less";

const { Content } = Layout;
const { Title } = Typography;

export default function VisaStatus() {
    return (
        <Layout className="tuixue-page">
            <TuixueHeader />
            <Content className="tuixue-content">
                <Title level={2} style={{ textAlign: "center", margin: "8px", padding: "8px" }}>
                    Visa Status Overview
                </Title>
                <Row>
                    <Col
                        xs={{ span: 24, push: 0 }}
                        sm={{ span: 22, push: 1 }}
                        md={{ span: 20, push: 2 }}
                        lg={{ span: 16, push: 4 }}
                        xl={{ span: 14, push: 5 }}
                    >
                        <VisaStatusTabs />
                    </Col>
                </Row>
            </Content>
        </Layout>
    );
}
