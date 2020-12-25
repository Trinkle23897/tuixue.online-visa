import React, { useState, useEffect, useMemo } from "react";
import PropTypes from "prop-types";
import { useSelector } from "react-redux";
import ReactEcharts from "echarts-for-react";
import { List, Row, Col, Button, Tooltip, Space, Card } from "antd";
import { MailOutlined, QqOutlined, EllipsisOutlined } from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { useScreenXS } from "../hooks";
import { getSingleVisaStatus } from "../services";
import { makeOverviewDetailSelector, makeNewestVisaStatusSelector } from "../redux/selectors";
import { getYMDFromISOString, getHMFromISOString } from "../utils/misc";
import "./VisaStatusOverview.less";

/**
 * IMPORTANT: This component/file is big and complex enough that we should refactor it into smaller components
 */

const overviewPropTypes = {
    overview: PropTypes.shape({
        visaType: PropTypes.string,
        embassyCode: PropTypes.string,
        earliestDate: PropTypes.arrayOf(PropTypes.string),
        latestDate: PropTypes.arrayOf(PropTypes.string),
    }).isRequired,
};

const TooltipBox = ({ children, title }) => (
    <Tooltip title={title}>
        <div style={{ width: "100%", height: "100%" }}>{children}</div>
    </Tooltip>
);
TooltipBox.propTypes = {
    title: PropTypes.string.isRequired,
    children: PropTypes.any.isRequired,
};

const OverviewNewest = ({ visaType, embassyCode }) => {
    const [t] = useTranslation();
    const newestVisaStatueSelector = useMemo(() => makeNewestVisaStatusSelector(visaType, embassyCode), [
        visaType,
        embassyCode,
    ]);
    const newestVisaStatus = useSelector(state => newestVisaStatueSelector(state));
    const { writeTime, availableDate } = newestVisaStatus || { writeTime: ["/"], availableDate: ["/"] };
    return (
        <Row justify="center" className="newest-inner-row">
            <Col xs={{ span: 11 }} md={{ span: 9 }}>
                {availableDate.join("/")}
            </Col>
            <Col span={2}>{t("at")}</Col>
            <Col xs={{ span: 11 }} md={{ span: 7 }}>
                {writeTime.length === 1 ? writeTime[0] : writeTime.slice(3).join(":")}
            </Col>
        </Row>
    );
};
OverviewNewest.propTypes = {
    visaType: PropTypes.string,
    embassyCode: PropTypes.string,
};

// This component can evolve into something VERY COMPLEX with subscription stuff.
// We may want to create a stand-alone component (e.g. OverviewWidget.j) file for it
const OverviewContentBar = ({ visaType, embassyCode, earliestDate, latestDate }) => {
    const [t] = useTranslation();
    return (
        <Row align="middle" className="ovreview-content-row" gutter={16}>
            <Col md={{ span: 3 }}>{t(embassyCode)}</Col>
            <Col md={{ span: 4 }}>
                <TooltipBox title={t("overviewEarliest")}>{earliestDate.join("/")}</TooltipBox>
            </Col>
            <Col md={{ span: 4 }}>
                <TooltipBox title={t("overviewLatest")}>{latestDate.join("/")}</TooltipBox>
            </Col>
            <Col md={{ span: 8 }}>
                <TooltipBox title={t("overviewNewest")}>
                    <OverviewNewest visaType={visaType} embassyCode={embassyCode} />
                </TooltipBox>
            </Col>
            <Col md={{ span: 5 }}>
                <Space direction="horizontal">
                    <TooltipBox title={t("overviewEmailIcon")}>
                        <Button icon={<MailOutlined />} shape="circle" onClick={() => {}} />
                    </TooltipBox>
                    <TooltipBox title={t("overviewQQIcon")}>
                        <Button icon={<QqOutlined />} shape="circle" onClick={() => {}} />
                    </TooltipBox>
                    <TooltipBox title={t("overviewAddtionalIcon")}>
                        <Button icon={<EllipsisOutlined rotate={90} />} shape="circle" onClick={() => {}} />
                    </TooltipBox>
                </Space>
            </Col>
        </Row>
    );
};
OverviewContentBar.propTypes = { ...overviewPropTypes.overview };

const OveriviewHeaderBar = () => {
    const [t] = useTranslation();
    return (
        <Row align="middle" className="ovreview-content-row" gutter={16}>
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

const OverviewContentCard = ({ visaType, embassyCode, earliestDate, latestDate }) => {
    const [t] = useTranslation();

    return (
        <Card
            title={t(embassyCode)}
            actions={[
                <TooltipBox title={t("overviewEmailIcon")}>
                    <Button icon={<MailOutlined />} shape="circle" onClick={() => {}} />
                </TooltipBox>,
                <TooltipBox title={t("overviewQQIcon")}>
                    <Button icon={<QqOutlined />} shape="circle" onClick={() => {}} />
                </TooltipBox>,
                <TooltipBox title={t("overviewAddtionalIcon")}>
                    <Button icon={<EllipsisOutlined rotate={90} />} shape="circle" onClick={() => {}} />
                </TooltipBox>,
            ]}
        >
            <Row>
                <Col span={9}>
                    <strong>{t("overviewEarliestDate")}: </strong>
                </Col>
                <Col span={15}>{earliestDate.join("/")}</Col>
                <Col span={9}>
                    <strong>{t("overviewLatestDate")}: </strong>
                </Col>
                <Col span={15}>{latestDate.join("/")}</Col>
                <Col span={9}>
                    <strong>{t("overviewNewestFetch")}: </strong>
                </Col>
                <Col span={15}>
                    <OverviewNewest visaType={visaType} embassyCode={embassyCode} />
                </Col>
            </Row>
        </Card>
    );
};
OverviewContentCard.propTypes = { ...overviewPropTypes.overview };

const OverviewChart = ({ visaType, embassyCode }) => {
    const [t] = useTranslation();
    const [xAxis, setXAxis] = useState([]);
    const [yAxis, setYAxis] = useState([]);
    useEffect(() => {
        const fetchData = async () => {
            const result = await getSingleVisaStatus(visaType, embassyCode, new Date());
            setXAxis(result.availableDates.map(({ writeTime }) => getHMFromISOString(writeTime)));
            setYAxis(result.availableDates.map(({ availableDate }) => getYMDFromISOString(availableDate)));
        };
        fetchData();
    }, [visaType, embassyCode]);
    return (
        <ReactEcharts
            option={{
                xAxis: {
                    type: "category",
                    data: xAxis,
                },
                yAxis: {
                    type: "time",
                },
                legend: {
                    data: [t(embassyCode)],
                },
                tooltip: {
                    trigger: "axis",
                    formatter: pack => {
                        const header = `${pack[0].name}<br/>`;
                        const content = pack
                            .map(({ marker, seriesName, data }) => `${marker}${seriesName}: ${data}`)
                            .join("<br>");
                        return header + content;
                    },
                },
                dataZoom: [
                    {
                        type: "slider",
                        height: 8,
                        bottom: 20,
                        borderColor: "transparent",
                        backgroundColor: "#e2e2e2",
                        handleIcon:
                            "M10.7,11.9H9.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4h1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7v-1.2h6.6z M13.3,22H6.7v-1.2h6.6z M13.3,19.6H6.7v-1.2h6.6z",
                        handleSize: 20,
                        handleStyle: {
                            shadowBlur: 6,
                            shadowOffsetX: 1,
                            shadowOffsetY: 2,
                            shadowColor: "#aaa",
                        },
                    },
                    {
                        type: "inside",
                    },
                ],
                series: [
                    {
                        name: t(embassyCode),
                        type: "line",
                        data: yAxis,
                    },
                ],
            }}
        />
    );
};
OverviewChart.propTypes = {
    visaType: PropTypes.string,
    embassyCode: PropTypes.string,
};

export default function VisaStatusOverviewList({ visaType }) {
    const overviewSelector = useMemo(() => makeOverviewDetailSelector(visaType), [visaType]);
    const overviewData = useSelector(state => overviewSelector(state));

    const screenXS = useScreenXS();

    return (
        <List
            itemLayout="vertical"
            dataSource={overviewData}
            header={!screenXS && <OveriviewHeaderBar />}
            renderItem={overview => (
                <List.Item key={overview.embassyCode}>
                    {screenXS ? <OverviewContentCard {...overview} /> : <OverviewContentBar {...overview} />}
                </List.Item>
            )}
        />
    );
}
VisaStatusOverviewList.propTypes = {
    visaType: PropTypes.string.isRequired,
};
