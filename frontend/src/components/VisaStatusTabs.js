import React, { createContext, useState } from "react";
import { Tabs, Typography } from "antd";
import VisaStatusOverview from "./VisaStatusOverview";
import "./VisaStatusTabs.less";

const { TabPane } = Tabs;
const { Title } = Typography;

export default function VisaStatusTabs() {
    return (
        <Tabs
            defaultActiveKey="F"
            type="card"
            size="large"
            renderTabBar={(props, DefaultTabBar) => <DefaultTabBar {...props} className="autofill-tab-bar" />}
            centered
        >
            {Array.from("FBHOL").map(visaType => (
                <TabPane tab={visaType} key={visaType}>
                    <Title level={2}>Visa Type {visaType}</Title>
                    <VisaStatusOverview visaType={visaType} />
                </TabPane>
            ))}
        </Tabs>
    );
}
