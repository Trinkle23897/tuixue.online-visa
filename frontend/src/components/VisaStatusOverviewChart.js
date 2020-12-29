import React, { useState, useEffect, useMemo } from "react";
import PropTypes from "prop-types";
import ReactEcharts from "echarts-for-react";
import { useSelector, useDispatch } from "react-redux";
import { useTranslation } from "react-i18next";
import { getSingleVisaStatus } from "../services";
import { makeFilterSelectorByVisaType } from "../redux/selectors";
import { fetchVisaStatusDetail } from "../redux/visastatusDetailSlice";
import { getDateFromISOString, getLocalDateTimeFromISOString } from "../utils/misc";

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
                xAxis: {
                    type: "category",
                    data: writeTime,
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
                series: availDateLst.map(({ embassyCode, availableDate }) => ({
                    name: t(embassyCode),
                    type: "line",
                    data: getDateFromISOString(availableDate),
                })),
            }}
        />
    );
};

OverviewChart.propTypes = {
    title: PropTypes.string.isRequired,
    writeTime: PropTypes.arrayOf(PropTypes.string.isRequired),
    availDateLst: PropTypes.arrayOf(
        PropTypes.shape({
            embassyCode: PropTypes.string.isRequired,
            availableDate: PropTypes.string.isRequired,
        }),
    ),
};

const mergeData = (chartType, detailData) => [[], []]; // TODO

export const OverviewChartByMinute = ({ visaType }) => {
    const filterSelector = useMemo(() => makeFilterSelectorByVisaType(visaType), [visaType]);
    const vsFilter = useSelector(state => filterSelector(state));
    const dispatch = useDispatch();

    useEffect(() => {
        vsFilter.map(embassyCode => dispatch(fetchVisaStatusDetail(visaType, embassyCode)));
    }, [visaType, vsFilter]);

    const detailData = useSelector(state => state.visastatusDetail[visaType]);
    const [writeTime, availDateLst] = mergeData("minute", detailData);
    return <OverviewChart title="OverMinute" writeTime={writeTime} availDateLst={availDateLst} />;
};
OverviewChartByMinute.propTypes = {
    visaType: PropTypes.string.isRequired,
};
