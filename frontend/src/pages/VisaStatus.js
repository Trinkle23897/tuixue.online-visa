import React from "react";
import { Layout, Typography } from "antd";
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
                <VisaStatusTabs />
            </Content>
        </Layout>
    );
}
