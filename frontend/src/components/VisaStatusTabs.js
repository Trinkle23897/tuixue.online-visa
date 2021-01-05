import React, { useState, useEffect } from "react";
import { useSelector, useDispatch } from "react-redux";
import { Tabs, Row, Col, Button, List, Divider } from "antd";
import { useTranslation } from "react-i18next";
import { MailOutlined, QqOutlined, LineChartOutlined } from "@ant-design/icons";
import { changeTabAndSetCookie } from "../redux/visastatusTabSlice";
import VisaStatusOverviewList from "./VisaStatusOverviewList";
import EmbassySelector from "./EmbassySelector";
import "./VisaStatusTabs.less";
import { OverviewChartByMinute, OverviewChartByDate } from "./VisaStatusOverviewList/OverviewChart";
import { setCookie, getCookie } from "../utils/cookie";
import { useScreenXS, useSubscriptionFormControl } from "../hooks";
import EmailSubscriptionForm from "./EmailSubscriptionForm";
import PostSubscriptionResult from "./PostSubscriptionResult";

const { TabPane } = Tabs;

const QQTGSubs = () => {
    const [t] = useTranslation();
    const [qqGroups, tgLink] = useSelector(state => [state.metadata.qqTgInfo.qq, state.metadata.qqTgInfo.tg]);
    // TODO qqGroup: domestic, hotGlobal, nonDomestic
    const qqGroupsStr = qqGroups.domestic
        .map((content, index) => ({
            index: `qqDomestic-${index}`,
            desc: `${t("QQGroupDomestic", { index: index + 1 })}${content}`,
        }))
        .concat(
            qqGroups.nonDomestic.map((content, index) => ({
                index: `qqNonDomestic-${index}`,
                desc: `${t("QQGroupNonDomestic", { index: index + 1 })}${content}`,
            })),
        );

    return (
        <>
            <p>
                {t("TGDomestic")}
                <a href={tgLink.domestic} target="_blank" rel="noreferrer">
                    {tgLink.domestic}
                </a>
            </p>
            <p>
                {t("TGNonDomestic")}
                <a href={tgLink.nonDomestic} target="_blank" rel="noreferrer">
                    {tgLink.nonDomestic}
                </a>
            </p>
            <Divider />
            <p>{t("QQDesc")}</p>
            <List
                itemLayout="vertical"
                dataSource={qqGroupsStr}
                renderItem={s => (
                    <List.Item key={s.index}>
                        <p>{s.desc}</p>
                    </List.Item>
                )}
                split={false}
            />
        </>
    );
};

const EmailSubs = () => {
    const [
        { form, formState, dispatchFormAction, formStateActions },
        pageInfo,
        postSubscription,
    ] = useSubscriptionFormControl();
    return formState.postingSubscription ? (
        <PostSubscriptionResult
            success={formState.postSuccessful}
            step="confirming"
            inSubscriptionPage={pageInfo.inSubscriptionPage}
        />
    ) : (
        <>
            <EmailSubscriptionForm
                formControl={{ form, formState }}
                pageInfo={pageInfo}
                cookieOption="email"
                onFinish={fieldValues => postSubscription(fieldValues)}
            />
            <Button onClick={() => form.submit()}>Submit</Button>
        </>
    );
};

export default function VisaStatusTabs() {
    const [t] = useTranslation();
    const dispatch = useDispatch();
    const visaType = useSelector(state => state.visastatusTab);
    const visaTypeDetails = useSelector(state => state.metadata.visaTypeDetails);
    const [func, setFunc] = useState("chart");
    const screenXS = useScreenXS();

    return (
        <>
            <Tabs
                activeKey={visaType}
                onChange={activeKey => dispatch(changeTabAndSetCookie(activeKey))}
                type="card"
                size="large"
                renderTabBar={(props, DefaultTabBar) => <DefaultTabBar {...props} className="autofill-tab-bar" />}
            >
                {Array.from("FBHOL").map(v => (
                    <TabPane tab={visaTypeDetails[v]} key={v} />
                ))}
            </Tabs>
            <Row gutter={[16, { xs: 16, md: 32 }]}>
                <Col span={24}>
                    <EmbassySelector visaType={visaType} />
                </Col>
                <Col span={24}>
                    <Tabs
                        activeKey={func}
                        onChange={activeKey => setFunc(activeKey)}
                        tabPosition={screenXS ? "top" : "left"}
                        centered={screenXS}
                    >
                        <TabPane tab={<LineChartOutlined />} key={"chart"}>
                            <OverviewChartByMinute visaType={visaType} />
                        </TabPane>
                        <TabPane tab={<MailOutlined />} key={"email"}>
                            <EmailSubs />
                        </TabPane>
                        {visaType === "F" && (
                            <TabPane tab={<QqOutlined />} key={"qqtg"}>
                                <QQTGSubs />
                            </TabPane>
                        )}
                    </Tabs>
                </Col>
                <Col span={24}>
                    <VisaStatusOverviewList visaType={visaType} />
                </Col>
            </Row>
        </>
    );
}
