import React, { useEffect, useMemo } from "react";
import PropTypes from "prop-types";
import ReactEcharts from "echarts-for-react";
import { useSelector, useDispatch } from "react-redux";
import { useTranslation } from "react-i18next";
import { makeFilterSelectorByVisaType } from "../redux/selectors";
import { fetchVisaStatusDetail } from "../redux/visastatusDetailSlice";
import { getTimeFromUTC } from "../utils/misc";

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

/**
 *
 * @param {string} title EChart title
 * @param {array} writeTime An array of ISODate string
 * @param {array} availDateLst An array with { embassyCode, availableDate }
 */
const OverviewChart = ({ title, writeTime, availDateLst }) => {
    const [t] = useTranslation();
    return (
        <ReactEcharts
            option={{
                title: {
                    text: title,
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

OverviewChart.propTypes = {
    title: PropTypes.string.isRequired,
    writeTime: PropTypes.arrayOf(PropTypes.number.isRequired),
    availDateLst: PropTypes.arrayOf(
        PropTypes.shape({
            embassyCode: PropTypes.string.isRequired,
            availableDates: PropTypes.arrayOf(PropTypes.string),
        }),
    ),
};

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

export const OverviewChartByMinute = ({ visaType }) => {
    const [t] = useTranslation();
    const filterSelector = useMemo(() => makeFilterSelectorByVisaType(visaType), [visaType]);
    const vsFilter = useSelector(state => filterSelector(state));
    const dispatch = useDispatch();

    useEffect(() => {
        vsFilter.map(embassyCode => dispatch(fetchVisaStatusDetail(visaType, embassyCode)));
    }, [visaType, vsFilter, dispatch]);

    const [writeTime, availDateLst] = useSelector(state => mergeDetailData(state.visastatusDetail[visaType], vsFilter));
    return <OverviewChart title={t("overMinuteChartTitle")} writeTime={writeTime} availDateLst={availDateLst} />;
};
OverviewChartByMinute.propTypes = {
    visaType: PropTypes.string.isRequired,
};
