import React, { useState, useEffect } from "react";
import { useSelector, useDispatch } from "react-redux";
import { Tabs, Row, Col, Button } from "antd";
import { useTranslation } from "react-i18next";
import { changeTabAndSetCookie } from "../redux/visastatusTabSlice";
import VisaStatusOverviewList from "./VisaStatusOverviewList";
import EmbassySelector from "./EmbassySelector";
import "./VisaStatusTabs.less";
import { OverviewChartByMinute, OverviewChartByDate } from "./VisaStatusOverviewList/OverviewChart";
import { setCookie, getCookie } from "../utils/cookie";

const { TabPane } = Tabs;

export default function VisaStatusTabs() {
    const [t] = useTranslation();
    const dispatch = useDispatch();
    const chosenKey = useSelector(state => state.visastatusTab);
    const visaTypeDetails = useSelector(state => state.metadata.visaTypeDetails);
    // const SelectOverviewType = () => <></>;

    return (
        <>
            <Tabs
                activeKey={chosenKey}
                onChange={activeKey => dispatch(changeTabAndSetCookie(activeKey))}
                type="card"
                size="large"
                renderTabBar={(props, DefaultTabBar) => <DefaultTabBar {...props} className="autofill-tab-bar" />}
            >
                {Array.from("FBHOL").map(visaType => (
                    <TabPane tab={visaTypeDetails[visaType]} key={visaType} />
                ))}
            </Tabs>
            <Row gutter={[16, { xs: 16, md: 32 }]}>
                <Col span={24}>
                    <EmbassySelector visaType={chosenKey} />
                </Col>
                <Col span={24}>
                    <OverviewChartByMinute visaType={chosenKey} />
                </Col>
                <Col span={24}>
                    <VisaStatusOverviewList visaType={chosenKey} />
                </Col>
            </Row>
        </>
    );
}
