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
                    <Col xs={0} sm={1} md={2} lg={4} xl={5} />
                    <Col xs={24} sm={22} md={20} lg={16} xl={14}>
                        <VisaStatusTabs />
                    </Col>
                    <Col xs={0} sm={1} md={2} lg={4} xl={5} />
                </Row>
            </Content>
        </Layout>
    );
}
