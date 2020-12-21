import React from "react";
import { useTranslation } from "react-i18next";
import { useSelector, useDispatch } from "react-redux";
import { Tabs, Typography, Row, Col } from "antd";
import { changeTab } from "../redux/visastatusTabSlice";
import VisaStatusOverviewList from "./VisaStatusOverview";
import EmbassySelector from "./EmbassySelector";
import "./VisaStatusTabs.less";

const { TabPane } = Tabs;
const { Title } = Typography;

export default function VisaStatusTabs() {
    const chosenKey = useSelector(state => state.visastatusTab);
    const dispatch = useDispatch();
    const [t, i18n] = useTranslation();

    return (
        <Tabs
            activeKey={chosenKey}
            onChange={activeKey => dispatch(changeTab({ activeKey }))}
            type="card"
            size="large"
            renderTabBar={(props, DefaultTabBar) => <DefaultTabBar {...props} className="autofill-tab-bar" />}
            centered
        >
            {Array.from("FBHOL").map(visaType => (
                <TabPane tab={visaType} key={visaType}>
                    <Row gutter={[16, { xs: 16, md: 32 }]}>
                        <Col span={24}>
                            <Title level={2}>{t("visaType", { visaType: visaType })}</Title>
                        </Col>
                        <Col span={24}>
                            <EmbassySelector visaType={visaType} />
                        </Col>
                        <Col span={24}>
                            <VisaStatusOverviewList visaType={visaType} />
                        </Col>
                    </Row>
                </TabPane>
            ))}
        </Tabs>
    );
}
