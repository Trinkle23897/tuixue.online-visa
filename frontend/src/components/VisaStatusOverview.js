import React, { useState, useEffect, useMemo } from "react";
import PropTypes from "prop-types";
import { useSelector } from "react-redux";
import ReactEcharts from "echarts-for-react";
import { List, Row, Col, Button, Tooltip } from "antd";
import { MailOutlined, QqOutlined, PlusOutlined } from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { getSingleVisaStatus } from "../services";
import { makeOverviewDetailSelector, makeNewestVisaStatusSelector } from "../redux/selectors";
import { getYMDFromISOString, getHMFromISOString } from "../utils/misc";

const overviewPropTypes = {
    overview: PropTypes.shape({
        visaType: PropTypes.string,
        embassyCode: PropTypes.string,
        earliestDate: PropTypes.arrayOf(PropTypes.string),
        latestDate: PropTypes.arrayOf(PropTypes.string),
    }).isRequired,
};

const rangeStr = (earliestDate, latestDate) =>
    earliestDate.length <= 1 ? "/" : `${earliestDate.slice(1).join("/")} ~ ${latestDate.slice(1).join("/")}`;

const newestStr = (availableDate, writeTime, at) =>
    writeTime.length <= 1 ? "/" : `${availableDate.join("/")} ${at} ${writeTime.slice(3).join(":")}`;

const OverviewNewest = ({ visaType, embassyCode }) => {
    const [t] = useTranslation();
    const newestVisaStatueSelector = useMemo(() => makeNewestVisaStatusSelector(visaType, embassyCode), [
        visaType,
        embassyCode,
    ]);
    const newestVisaStatus = useSelector(state => newestVisaStatueSelector(state));
    const { writeTime, availableDate } = newestVisaStatus || { writeTime: ["/"], availableDate: ["/"] };
    return (
        <Tooltip title={t("overviewNewest")}>
            <Col xs={{ span: 12 }} md={{ span: 5 }} style={{ textAlign: "right" }}>
                {newestStr(availableDate, writeTime, t("at"))}
            </Col>
        </Tooltip>
    );
};
OverviewNewest.propTypes = {
    visaType: PropTypes.string,
    embassyCode: PropTypes.string,
};

// This component can evolve into something VERY COMPLEX with subscription stuff.
// We may want to create a stand-alone component (e.g. OverviewWidget.j) file for it
const OverviewContent = ({ overview }) => {
    const [t] = useTranslation();
    return (
        <Row align="middle" justify="space-around">
            <Col xs={{ span: 12 }} md={{ span: 2 }} style={{ textAlign: "center" }}>
                {t(overview.embassyCode)}
            </Col>
            <Tooltip title={t("overviewRange")}>
                <Col xs={{ span: 12 }} md={{ span: 5 }} style={{ textAlign: "center" }}>
                    {rangeStr(overview.earliestDate, overview.latestDate)}
                </Col>
            </Tooltip>
            <OverviewNewest visaType={overview.visaType} embassyCode={overview.embassyCode} />
            <Col md={{ span: 1 }}>
                <Tooltip title={t("overviewPlusIcon")}>
                    <Button icon={<PlusOutlined />} shape="circle" onClick={() => {}} />
                </Tooltip>
            </Col>
            <Col md={{ span: 1 }}>
                <Tooltip title={t("overviewEmailIcon")}>
                    <Button
                        icon={<MailOutlined />}
                        shape="circle"
                        onClick={() => console.log(`Click subscription button of ${t(overview.embassyCode)}`)}
                    />
                </Tooltip>
            </Col>
            <Col md={{ span: 1 }}>
                <Tooltip title={t("overviewQQIcon")}>
                    <Button
                        icon={<QqOutlined />}
                        shape="circle"
                        onClick={() => console.log(`Click QQ button of ${t(overview.embassyCode)}`)}
                    />
                </Tooltip>
            </Col>
        </Row>
    );
};
OverviewContent.propTypes = overviewPropTypes;

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

const VisaStatusOverviewListItem = ({ overview }) => (
    <List.Item
        style={{
            marginBottom: 12,
            backgroundColor: "#FFFFFF",
        }}
    >
        <OverviewContent overview={overview} />
    </List.Item>
);
VisaStatusOverviewListItem.propTypes = overviewPropTypes;

export default function VisaStatusOverviewList({ visaType }) {
    const overviewSelector = useMemo(() => makeOverviewDetailSelector(visaType), [visaType]);
    const overviewData = useSelector(state => overviewSelector(state));

    return (
        <List
            itemLayout="vertical"
            dataSource={overviewData}
            renderItem={overview => <VisaStatusOverviewListItem key={overview.embassyCode} overview={overview} />}
        />
    );
}
VisaStatusOverviewList.propTypes = {
    visaType: PropTypes.string.isRequired,
};
