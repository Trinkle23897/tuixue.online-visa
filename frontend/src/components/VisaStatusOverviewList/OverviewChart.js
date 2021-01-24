import React, { useMemo } from "react";
import PropTypes from "prop-types";
import { notification } from "antd";
import ReactEcharts from "echarts-for-react";
import { useSelector, useDispatch } from "react-redux";
import { useTranslation } from "react-i18next";
import { makeMinuteChartData, makeDateChartData } from "../../redux/selectors";
import { getTimeFromUTC, getDateFromISOString } from "../../utils/misc";
import { fetchVisaStatusDetail } from "../../redux/visastatusDetailSlice";
import { fetchVisaStatusOverview } from "../../redux/visastatusOverviewSlice";

const dataZoom = [
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
];

export const OverviewChartByMinute = ({ visaType }) => {
    const [t] = useTranslation();
    const dispatch = useDispatch();
    const minuteChartDataSelector = useMemo(() => makeMinuteChartData(visaType), [visaType]);
    const [writeTime, availDateLst] = useSelector(state => minuteChartDataSelector(state));
    return (
        <ReactEcharts
            notMerge
            option={{
                title: {
                    text: "",
                },
                xAxis: {
                    type: "category",
                    data: writeTime.map(u => getTimeFromUTC(u).slice(0, -1).join(":")),
                },
                yAxis: {
                    type: "time",
                    name: t("overview.earliestDate"),
                    nameLocation: "middle",
                    nameGap: 50,
                },
                legend: {
                    data: availDateLst.map(({ embassyCode }) => t(embassyCode)),
                },
                tooltip: {
                    trigger: "axis",
                    formatter: pack => {
                        const header = `${t("overMinuteChartTitle")}: ${pack[0].name}<br/>`;
                        const content = pack
                            .map(({ marker, seriesName, data }) => `${marker}${seriesName}: ${data}`)
                            .join("<br>");
                        return header + content;
                    },
                },
                toolbox: {
                    show: true,
                    feature: {
                        myRefresh: {
                            title: t("Refresh"),
                            icon:
                                "M3.8,33.4 M47,18.9h9.8V8.7 M56.3,20.1 C52.1,9,40.5,0.6,26.8,2.1C12.6,3.7,1.6,16.2,2.1,30.6 M13,41.1H3.1v10.2 M3.7,39.9c4.2,11.1,15.8,19.5,29.5,18 c14.2-1.6,25.2-14.1,24.7-28.5",
                            onclick: () => {
                                dispatch(fetchVisaStatusOverview(visaType));
                                dispatch(fetchVisaStatusDetail(visaType));
                                notification.open({
                                    message: t("refreshDone"),
                                });
                            },
                        },
                    },
                },
                dataZoom,
                series: availDateLst.map(({ embassyCode, availableDates }) => ({
                    name: t(embassyCode),
                    type: "line",
                    data: availableDates,
                })),
            }}
        />
    );
};
OverviewChartByMinute.propTypes = {
    visaType: PropTypes.string.isRequired,
};

const renderItem = (params, api) => {
    const xValue = api.value(0);
    const earliestPoint = api.coord([xValue, api.value(1)]);
    const latestPoint = api.coord([xValue, api.value(2)]);
    // const halfWidth = api.size([1, 0])[0] * 0.35;
    const style = api.style({ stroke: api.visual("color") });
    return {
        type: "group",
        children: [
            {
                type: "line",
                shape: {
                    x1: earliestPoint[0],
                    y1: earliestPoint[1],
                    x2: latestPoint[0],
                    y2: latestPoint[1],
                },
                style,
            },
        ],
    };
};

export const OverviewChartByDate = ({ visaType, embassyCode }) => {
    const [t] = useTranslation();
    const dateChartDataSelector = useMemo(() => makeDateChartData(visaType, embassyCode), [visaType, embassyCode]);
    const [overviewData, earliestDiffMean, latestDiffMean] = useSelector(state => dateChartDataSelector(state));
    return (
        <>
            <ReactEcharts
                notMerge
                option={{
                    title: {
                        text: "",
                    },
                    legend: {
                        data: [],
                    },
                    dataZoom,
                    xAxis: {
                        type: "category",
                        data: overviewData.map(d => getDateFromISOString(d[1]).join("-")),
                    },
                    yAxis: {
                        type: "time",
                        name: `${t("overview.earliestDate")} ~ ${t("overview.latestDate")}`,
                        nameLocation: "middle",
                        nameGap: 50,
                    },
                    tooltip: {
                        trigger: "axis",
                        formatter: pack => {
                            const header = `${pack[0].name}<br/>`;
                            const rangeStr = (earliestDate, latestDate) => {
                                if (earliestDate === null && latestDate === null) return "/";
                                const earliestDateStr = getDateFromISOString(earliestDate).join("/");
                                const latestDateStr = getDateFromISOString(latestDate).join("/");
                                if (earliestDateStr === latestDateStr) return earliestDateStr;
                                return `${earliestDateStr} ~ ${latestDateStr}`;
                            };
                            const content = pack
                                .filter(e => e.componentSubType === "custom")
                                .map(
                                    ({ marker, seriesName, data }) =>
                                        `${marker}${seriesName}: ${rangeStr(data[1], data[2])}`,
                                )
                                .join("<br>");
                            return header + content;
                        },
                    },
                    series: [
                        {
                            name: t(embassyCode),
                            type: "line",
                            data: overviewData.map(d => [d[0], d[3]]),
                            encode: {
                                x: [0],
                                y: [1],
                            },
                        },
                        {
                            name: t(embassyCode),
                            type: "custom",
                            renderItem,
                            dimensions: [null, "Earliest", "Latest"],
                            data: overviewData.map(d => [d[0], d[2], d[3]]),
                            encode: {
                                x: [0],
                                y: [1, 2],
                            },
                        },
                    ],
                }}
            />
            <p style={{ textAlign: "center" }}>
                {t("overDateChartTitle", { embassyName: t(embassyCode) })}
                {earliestDiffMean === null
                    ? t("overDateChartSubtitleNull")
                    : t("overDateChartSubtitle", { earliestDiffMean, latestDiffMean })}
            </p>
        </>
    );
};
OverviewChartByDate.propTypes = {
    visaType: PropTypes.string.isRequired,
    embassyCode: PropTypes.string.isRequired,
};
