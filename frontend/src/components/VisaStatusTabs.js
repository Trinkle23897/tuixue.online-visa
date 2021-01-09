import React, { useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { Tabs, Row, Col, Button, List, Divider, Tooltip } from "antd";
import { useTranslation } from "react-i18next";
import { MailOutlined, QqOutlined, LineChartOutlined } from "@ant-design/icons";
import { changeTabAndSetCookie } from "../redux/visastatusTabSlice";
import { nonDomesticEmbassyInDefaultFilterSelector } from "../redux/selectors";
import VisaStatusOverviewList from "./VisaStatusOverviewList";
import EmbassySelector from "./EmbassySelector";
import "./VisaStatusTabs.less";
import { OverviewChartByMinute } from "./VisaStatusOverviewList/OverviewChart";
import { useScreenXS, useSubscriptionFormControl } from "../hooks";
import EmailSubscriptionForm from "./EmailSubscriptionForm";
import PostSubscriptionResult from "./PostSubscriptionResult";

const { TabPane } = Tabs;

const QQTGSubs = () => {
    const [t] = useTranslation();
    const [qqGroups, tgLink] = useSelector(state => [state.metadata.qqTgInfo.qq, state.metadata.qqTgInfo.tg]);
    const nonDomesticEmbassyInDefaultFilter = useSelector(state => nonDomesticEmbassyInDefaultFilterSelector(state));
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
            <p>{t("QQDescDomestic")}</p>
            {qqGroups.domestic.map((content, index) => (
                <p key={`qqDomestic-${content}`}>{`${t("QQGroupDomestic", { index: index + 1 })}${content}`}</p>
            ))}
            <Divider />
            <p>{t("QQDescNonDomestic", { cities: nonDomesticEmbassyInDefaultFilter.map(e => t(e)).join(" / ") })}</p>
            {qqGroups.nonDomestic.map((content, index) => (
                <p key={`qqNonDomestic-${content}`}>{`${t("QQGroupNonDomestic", { index: index + 1 })}${content}`}</p>
            ))}
        </>
    );
};

const EmailSubs = () => {
    const [t] = useTranslation();
    const [{ form, formState }, pageInfo, postSubscription] = useSubscriptionFormControl();
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
            <Button onClick={() => form.submit()}>{t("emailForm.subscribe")}</Button>
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
                        <TabPane
                            tab={
                                <Tooltip title={t("overMinuteChartTitle")}>
                                    <LineChartOutlined />
                                </Tooltip>
                            }
                            key={"chart"}
                        >
                            <OverviewChartByMinute visaType={visaType} />
                        </TabPane>
                        <TabPane
                            tab={
                                <Tooltip title={t("overviewEmailIcon")}>
                                    <MailOutlined />
                                </Tooltip>
                            }
                            key={"email"}
                        >
                            <EmailSubs />
                        </TabPane>
                        {visaType === "F" && (
                            <TabPane
                                tab={
                                    <Tooltip title={t("overviewQQIcon")}>
                                        <QqOutlined />
                                    </Tooltip>
                                }
                                key={"qqtg"}
                            >
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
