import React from "react";
import { Layout, Typography, Row, Col } from "antd";
import { DiscussionEmbed } from "disqus-react";
import { useTranslation } from "react-i18next";
import { TuixueHeader, VisaStatusTabs } from "../components";
import { useScreenXS } from "../hooks";
import "./VisaStatus.less";

const { Content } = Layout;
const { Title } = Typography;

export default function VisaStatus() {
    const [t] = useTranslation();
    const screenXS = useScreenXS();

    const paddingStyle = ["Left", "Rgiht"].reduce(
        (padding, side) => ({ ...padding, [`padding${side}`]: screenXS ? 8 : 0 }),
        {},
    );

    return (
        <Layout className="tuixue-page">
            <TuixueHeader />
            <Content className="tuixue-content" style={paddingStyle}>
                <Title level={2} style={{ textAlign: "center", margin: "8px", padding: "8px" }}>
                    {t("overviewTitle")}
                </Title>
                <Row>
                    <Col
                        xs={{ span: 22, push: 1 }}
                        sm={{ span: 22, push: 1 }}
                        md={{ span: 20, push: 2 }}
                        lg={{ span: 16, push: 4 }}
                        xl={{ span: 14, push: 5 }}
                    >
                        <VisaStatusTabs />
                        <DiscussionEmbed shortname="tuixue-online" />
                    </Col>
                </Row>
            </Content>
        </Layout>
    );
}
