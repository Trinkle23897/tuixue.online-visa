import React, { useState } from "react";
import { Layout, Typography, Row, Col, Tabs } from "antd";
import { DiscussionEmbed } from "disqus-react";
import { useTranslation } from "react-i18next";
import { TuixueHeader, VisaStatusTabs } from "../components";
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
                        <Tabs centered activeKey={disqusType} onChange={activeKey => setDisqusType(activeKey)}>
                            <TabPane tab={t("disqusDomestic")} key="visa" />
                            <TabPane tab={t("disqusGlobal")} key="global" />
                        </Tabs>
                        <DiscussionEmbed
                            shortname="tuixue-online"
                            config={{
                                url: `https://tuixue.online/${disqusType}/`,
                                identifier: disqusType === "visa" ? "tuixue-online" : "global",
                                title: "tuixue-online",
                            }}
                        >
                            {t("disqusLoadFail")}
                        </DiscussionEmbed>
                    </Col>
                </Row>
            </Content>
        </Layout>
    );
}
