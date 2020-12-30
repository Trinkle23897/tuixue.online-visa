import React, { useEffect, useMemo } from "react";
import PropTypes from "prop-types";
import ReactEcharts from "echarts-for-react";
import { useSelector, useDispatch } from "react-redux";
import { useTranslation } from "react-i18next";
import {
    makeFilterSelectorByVisaType,
    makeDetailSelectorByVisaType,
    makeOverviewSpanSelectorByVisaType,
} from "../redux/selectors";
import { fetchVisaStatusDetail } from "../redux/visastatusDetailSlice";
import { getTimeFromUTC, getDateFromISOString } from "../utils/misc";

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

const mergeDetailData = (rawData, vsFilter) => {
    const detailData = vsFilter.map(embassyCode => ({ embassyCode, data: rawData[embassyCode] || [] }));
    let writeTimeAll = [];
    detailData.map(({ data }) => writeTimeAll.push(...data.map(({ writeTime }) => writeTime - (writeTime % 60000))));
    writeTimeAll = Array.from(new Set(writeTimeAll));
    writeTimeAll.sort();
    const availDateLst = [];
    detailData.map(({ embassyCode, data }) => {
        let dataIndex = 0;
        const availableDates = writeTimeAll.map(writeTimeRef => {
            if (dataIndex >= data.length) return null;
            const { writeTime, availableDate } = data[dataIndex];
            const writeTimeData = writeTime - (writeTime % 60000); // exclude SS
            if (writeTimeRef === writeTimeData) {
                dataIndex += 1;
                return availableDate.join("/");
            }
            if (dataIndex > 0 && writeTime - writeTimeRef < 60000 * 5) {
                // within 5 minutes, automatically fill the gap
                return data[dataIndex - 1].availableDate.join("/");
            }
            return null;
        });
        return availDateLst.push({ embassyCode, availableDates });
    });
    return [writeTimeAll, availDateLst];
};

const mergeOverviewData = (rawData, vsFilter) =>
    rawData
        .slice()
        .reverse()
        .map(({ date, overview }, index) => {
            const earliestDateObj = {};
            const latestDateObj = {};
            overview.forEach(({ embassyCode, earliestDate, latestDate }) => {
                earliestDateObj[embassyCode] = earliestDate;
                latestDateObj[embassyCode] = latestDate;
            });
            const earliestDateLst = vsFilter.map(embassyCode => earliestDateObj[embassyCode] || null);
            const latestDateLst = vsFilter.map(embassyCode => latestDateObj[embassyCode] || null);
            return [index, getDateFromISOString(date).join("-")].concat(earliestDateLst).concat(latestDateLst);
        });

export const OverviewChartByMinute = ({ visaType }) => {
    const [t] = useTranslation();
    const filterSelector = useMemo(() => makeFilterSelectorByVisaType(visaType), [visaType]);
    const detailSelector = useMemo(() => makeDetailSelectorByVisaType(visaType), [visaType]);
    const vsFilter = useSelector(state => filterSelector(state));
    const dispatch = useDispatch();

    useEffect(() => {
        vsFilter.map(embassyCode => dispatch(fetchVisaStatusDetail(visaType, embassyCode)));
    }, [visaType, vsFilter, dispatch]);

    const [writeTime, availDateLst] = useSelector(state =>
        mergeDetailData(detailSelector(state), filterSelector(state)),
    );
    return (
        <ReactEcharts
            option={{
                title: {
                    text: t("overMinuteChartTitle"),
                },
                xAxis: {
                    type: "category",
                    data: writeTime.map(u => getTimeFromUTC(u).slice(0, -1).join(":")),
                },
                yAxis: {
                    type: "time",
                },
                legend: {
                    data: availDateLst.map(({ embassyCode }) => t(embassyCode)),
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
            // {
            //     type: "line",
            //     shape: {
            //         x1: earliestPoint[0] - halfWidth,
            //         y1: earliestPoint[1],
            //         x2: earliestPoint[0] + halfWidth,
            //         y2: earliestPoint[1],
            //     },
            //     style,
            // },
            // {
            //     type: "line",
            //     shape: {
            //         x1: latestPoint[0] - halfWidth,
            //         y1: latestPoint[1],
            //         x2: latestPoint[0] + halfWidth,
            //         y2: latestPoint[1],
            //     },
            //     style,
            // },
        ],
    };
};

export const OverviewChartByDate = ({ visaType }) => {
    const [t] = useTranslation();
    const filterSelector = useMemo(() => makeFilterSelectorByVisaType(visaType), [visaType]);
    const spanSelector = useMemo(() => makeOverviewSpanSelectorByVisaType(visaType), [visaType]);
    const vsFilter = useSelector(state => filterSelector(state));
    const overviewData = useSelector(state => mergeOverviewData(spanSelector(state), vsFilter));
    return (
        <ReactEcharts
            option={{
                title: {
                    text: t("overDateChartTitle"),
                },
                legend: {
                    data: vsFilter.map(embassyCode => t(embassyCode)),
                },
                dataZoom,
                xAxis: {
                    type: "category",
                    data: overviewData.map(d => d[1]),
                },
                yAxis: {
                    type: "time",
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
                series: vsFilter
                    .map((embassyCode, index) => [
                        {
                            name: t(embassyCode),
                            type: "line",
                            data: overviewData.map(d => [d[0], d[index + 2 + vsFilter.length]]),
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
                            data: overviewData.map(d => [d[0], d[index + 2], d[index + 2 + vsFilter.length]]),
                            encode: {
                                x: [0],
                                y: [1, 2],
                            },
                        },
                    ])
                    .flat(),
            }}
        />
    );
};
OverviewChartByDate.propTypes = {
    visaType: PropTypes.string.isRequired,
};
