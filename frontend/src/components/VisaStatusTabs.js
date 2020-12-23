import React from "react";
import { useSelector, useDispatch } from "react-redux";
import { Tabs, Row, Col } from "antd";
import { changeTabAndSetCookie } from "../redux/visastatusTabSlice";
import VisaStatusOverviewList from "./VisaStatusOverview";
import EmbassySelector from "./EmbassySelector";
import "./VisaStatusTabs.less";

const { TabPane } = Tabs;

export default function VisaStatusTabs() {
    const chosenKey = useSelector(state => state.visastatusTab);
    const dispatch = useDispatch();

    return (
        <Tabs
            activeKey={chosenKey}
            onChange={activeKey => dispatch(changeTabAndSetCookie(activeKey))}
            type="card"
            size="large"
            renderTabBar={(props, DefaultTabBar) => <DefaultTabBar {...props} className="autofill-tab-bar" />}
            centered
        >
            {Array.from("FBHOL").map(visaType => (
                <TabPane tab={visaType} key={visaType}>
                    <Row gutter={[16, { xs: 16, md: 32 }]}>
                        {/* <Col span={24}>
                            <Title level={2}>{t("visaType", { visaType: visaType })}</Title>
                        </Col> */}
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
