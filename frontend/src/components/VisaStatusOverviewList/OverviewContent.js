import React, { useMemo, useState } from "react";
import PropTypes from "prop-types";
import { useSelector } from "react-redux";
import ReactMarkdown from "react-markdown";
import { Row, Col, Button, Tooltip, Collapse, Tag } from "antd";
import { PlusOutlined, MailOutlined, QqOutlined } from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { useScreenXS } from "../../hooks";
import { makeNewestVisaStatusSelector, makeCountryCodeSelector } from "../../redux/selectors";
import { getTimeFromUTC } from "../../utils/misc";
import { overviewAttrProps, newestOverviewProps, overviewProps, dropdownProps } from "./overviewPropTypes";
import { OverviewChartByDate } from "./OverviewChart";
import "./VisaStatusOverview.less";

const { Panel } = Collapse;

const DropdownContent = ({ visaType, embassyCode }) => {
    const [t] = useTranslation();
    const countryCodeSelector = useMemo(() => makeCountryCodeSelector(embassyCode), [embassyCode]);
    const countryCode = useSelector(state => countryCodeSelector(state));
    const additionalInfoKey = `additionalInfo${countryCode}`;
    const additionalInfoMarkdown = t(additionalInfoKey) === additionalInfoKey ? "" : t(additionalInfoKey);
    return (
        <Row>
            <Col span={24}>
                <OverviewChartByDate visaType={visaType} embassyCode={embassyCode} />
            </Col>
            <Col span={24}>
                <p style={{ textAlign: "center" }}>{t("overDateChartTitle", { embassyName: t(embassyCode) })}</p>
            </Col>
            {visaType === "F" && (
                <Col span={24}>
                    <h2>{t("overviewQQIcon")}</h2>
                    <p>
                        {t("additionalInfoTop.part1")}
                        <QqOutlined />
                        {t("additionalInfoTop.part2")}
                    </p>
                </Col>
            )}
            <Col span={24}>
                <h2>{t("overviewEmailIcon")}</h2>
                <p>
                    {t("additionalInfoTop.part1")}
                    <MailOutlined />
                    {t("additionalInfoTop.part2")}
                </p>
            </Col>
            <Col span={24}>
                <ReactMarkdown>{additionalInfoMarkdown}</ReactMarkdown>
            </Col>
        </Row>
    );
};
DropdownContent.propTypes = dropdownProps;

const ContentBar = ({ embassyCode, earliestDate, latestDate, newest, visaType }) => {
    const [t] = useTranslation();
    const [cardDrop, setCardDrop] = useState(false);
    const { writeTime, availableDate } = newest;

    const DropdownControlBtn = () => (
        <Tooltip title={t("overviewAddtionalIcon")}>
            <Button
                icon={<PlusOutlined rotate={cardDrop ? 45 : 0} />}
                shape="circle"
                onClick={() => setCardDrop(!cardDrop)}
            />
        </Tooltip>
    );

    const BriefOverview = () => (
        <Row align="middle" className="ovreview-content-row" gutter={32}>
            <Col md={{ span: 3 }}>{t(embassyCode)}</Col>
            <Col md={{ span: 4 }}>
                <Tooltip title={t("overviewEarliest")}>{earliestDate.join("/")}</Tooltip>
            </Col>
            <Col md={{ span: 4 }}>
                <Tooltip title={t("overviewLatest")}>{latestDate.join("/")}</Tooltip>
            </Col>
            <Col md={{ span: 8 }}>
                <Tooltip title={t("overviewNewest")}>
                    <Row justify="center" align="middle">
                        <Col xs={{ span: 11 }} md={{ span: 9 }}>
                            {availableDate.join("/")}
                        </Col>
                        <Col xs={{ span: 13 }} md={{ span: 9 }}>
                            <Tag>{`${t("at")} ${
                                writeTime === "/" ? writeTime : getTimeFromUTC(writeTime).join(":")
                            }`}</Tag>
                        </Col>
                    </Row>
                </Tooltip>
            </Col>
            <Col md={{ span: 5 }}>
                <DropdownControlBtn />
            </Col>
        </Row>
    );

    return (
        <Collapse
            activeKey={cardDrop ? [embassyCode] : []}
            className="overview-dropdown-card"
            ghost
            onChange={() => setCardDrop(!cardDrop)}
        >
            <Panel key={embassyCode} header={<BriefOverview />} showArrow={false}>
                <DropdownContent embassyCode={embassyCode} visaType={visaType} />
            </Panel>
        </Collapse>
    );
};
ContentBar.propTypes = { ...overviewAttrProps, ...newestOverviewProps };

const ContentCard = ({ embassyCode, earliestDate, latestDate, newest, visaType }) => {
    const { t } = useTranslation();
    const [cardDrop, setCardDrop] = useState(false);
    const { writeTime, availableDate } = newest;

    const DropdownControlBtn = () => (
        <Tooltip title={t("overviewAddtionalIcon")}>
            <Button
                icon={<PlusOutlined rotate={cardDrop ? 45 : 0} />}
                shape="circle"
                onClick={() => setCardDrop(!cardDrop)}
            />
        </Tooltip>
    );

    const BriefOverview = () => (
        <Row align="middle">
            <Col span={8}>{t(embassyCode)}</Col>
            <Col span={cardDrop ? 0 : 8}>{availableDate.join("/")}</Col>
            <Col span={cardDrop ? 16 : 8}>
                <Row justify="end" align="middle">
                    <Col>
                        <DropdownControlBtn />
                    </Col>
                </Row>
            </Col>
        </Row>
    );

    return (
        <Collapse
            activeKey={cardDrop ? [embassyCode] : []}
            className="overview-dropdown-card"
            ghost
            onChange={() => setCardDrop(!cardDrop)}
        >
            <Panel key={embassyCode} header={<BriefOverview />} showArrow={false}>
                <Row>
                    <Col span={8}>
                        <strong>{t("overviewEarliestDate")}: </strong>
                    </Col>
                    <Col span={8} className="content-data">
                        {earliestDate.join("/")}
                    </Col>
                    <Col span={8} />
                    <Col span={8}>
                        <strong>{t("overviewLatestDate")}: </strong>
                    </Col>
                    <Col span={8} className="content-data">
                        {latestDate.join("/")}
                    </Col>
                    <Col span={8} />
                    <Col span={8}>
                        <strong>{t("overviewNewestFetch")}: </strong>
                    </Col>
                    <Col span={16} className="content-data">
                        <Row justify="center" align="middle">
                            <Col span={12}>{availableDate.join("/")}</Col>
                            <Col span={12}>
                                <Tag>{`${t("at")} ${
                                    writeTime === "/" ? writeTime : getTimeFromUTC(writeTime).join(":")
                                }`}</Tag>
                            </Col>
                        </Row>
                    </Col>
                </Row>
                <DropdownContent embassyCode={embassyCode} visaType={visaType} />
            </Panel>
        </Collapse>
    );
};
ContentCard.propTypes = { ...overviewAttrProps, ...newestOverviewProps };

const HeaderBar = () => {
    const [t] = useTranslation();
    return (
        <Row align="middle" className="ovreview-header bar" gutter={16}>
            <Col xs={{ span: 0 }} md={{ span: 3 }}>
                <strong>{t("Location")}</strong>
            </Col>
            <Col xs={{ span: 0 }} md={{ span: 4 }}>
                <strong>{t("overviewEarliestDate")}</strong>
            </Col>
            <Col xs={{ span: 0 }} md={{ span: 4 }}>
                <strong>{t("overviewLatestDate")}</strong>
            </Col>
            <Col xs={{ span: 0 }} md={{ span: 8 }}>
                <strong>{t("overviewNewestFetch")}</strong>
            </Col>
            <Col xs={{ span: 0 }} md={{ span: 5 }}>
                <strong>{t("overviewActions")}</strong>
            </Col>
        </Row>
    );
};

const HeaderCard = () => {
    const [t] = useTranslation();
    return (
        <Row align="middle" className="ovreview-header card">
            <Col span={8}>
                <strong>{t("Location")}</strong>
            </Col>
            <Col span={8}>
                <strong>{t("overviewNewestFetch")}</strong>
            </Col>
            <Col span={8}>
                <strong>{t("overviewActions")}</strong>
            </Col>
        </Row>
    );
};

export const OverviewHeader = () => {
    const screenXS = useScreenXS();
    return screenXS ? <HeaderCard /> : <HeaderBar />;
};

export const OverviewContent = ({ overview }) => {
    const screenXS = useScreenXS();
    const newestVisaStatueSelector = useMemo(
        () => makeNewestVisaStatusSelector(overview.visaType, overview.embassyCode),
        [overview],
    );
    const newestVisaStatus = useSelector(state => newestVisaStatueSelector(state));
    const newest = newestVisaStatus || { writeTime: "/", availableDate: ["/"] };

    return screenXS ? <ContentCard {...overview} newest={newest} /> : <ContentBar {...overview} newest={newest} />;
};
OverviewContent.propTypes = overviewProps;
