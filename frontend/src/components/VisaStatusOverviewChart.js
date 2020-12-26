import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import ReactEcharts from "echarts-for-react";
import { useTranslation } from "react-i18next";
import { getSingleVisaStatus } from "../services";
import { getDateFromISOString, getTimeFromISOString } from "../utils/misc";

export default function OverviewChart({ visaType, embassyCode }) {
    const [t] = useTranslation();
    const [xAxis, setXAxis] = useState([]);
    const [yAxis, setYAxis] = useState([]);
    useEffect(() => {
        const fetchData = async () => {
            const result = await getSingleVisaStatus(visaType, embassyCode, new Date());
            setXAxis(
                result.availableDates.map(({ writeTime }) => getTimeFromISOString(writeTime).slice(0, 2).join("/")),
            );
            setYAxis(result.availableDates.map(({ availableDate }) => getDateFromISOString(availableDate).join("/")));
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
}
OverviewChart.propTypes = {
    visaType: PropTypes.string,
    embassyCode: PropTypes.string,
};
