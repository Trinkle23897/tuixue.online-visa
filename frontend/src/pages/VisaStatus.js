import React, { useState } from "react";
import { Layout, Typography, Row, Col, Tabs } from "antd";
import { DiscussionEmbed } from "disqus-react";
import { useTranslation } from "react-i18next";
import { TuixueHeader, VisaStatusTabs, CounterFooter } from "../components";
import "./VisaStatus.less";

const { Content } = Layout;
const { Title } = Typography;
const { TabPane } = Tabs;

export default function VisaStatus() {
    const [t] = useTranslation();
    const [disqusType, setDisqusType] = useState("visa");
    return (
        <Layout className="tuixue-page">
            <TuixueHeader />
            <Content className="tuixue-content">
                <Title level={2} style={{ textAlign: "center", margin: "8px", padding: "8px" }}>
                    {t("overview.title")}
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
                        <CounterFooter />
                        <Tabs centered activeKey={disqusType} onChange={activeKey => setDisqusType(activeKey)}>
                            <TabPane tab={t("disqus.domestic")} key="visa" />
                            <TabPane tab={t("disqus.global")} key="global" />
                        </Tabs>
                        <DiscussionEmbed
                            shortname="tuixue-online"
                            config={{
                                url: `https://tuixue.online/${disqusType}/`,
                                identifier: disqusType === "visa" ? "tuixue-online" : "global",
                                title: "tuixue-online",
                            }}
                        >
                            {t("disqus.loadFail")}
                        </DiscussionEmbed>
                    </Col>
                </Row>
            </Content>
        </Layout>
    );
}
