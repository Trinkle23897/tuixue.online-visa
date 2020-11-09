import React, { useEffect, useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { InfoCircleFilled } from "@ant-design/icons";
import { notification } from "antd";
import { fetchLatestWritten } from "../redux/latestWrittenSlice";

export default function NotificationPopUp() {
    const dispatch = useDispatch();
    const latestWrittenFilter = useSelector(state => state.latestWritten.filter);
    const latestWrittenData = useSelector(state => state.latestWritten.latestWritten);

    useEffect(() => {
        const intervalId = setInterval(() => dispatch(fetchLatestWritten()), 5000);
        return () => clearInterval(intervalId);
    }, [dispatch, latestWrittenFilter]);

    useEffect(() => {
        if (latestWrittenData.length !== 0) {
            notification.open({
                message: "New Avaialbe Visa Appointment!",
                description: `Current latest written: ${JSON.stringify(latestWrittenData)}`,
                duration: 1.5,
                icon: <InfoCircleFilled size="large" />,
            });
        }
    }, [latestWrittenData]);

    return <div>{latestWrittenData}</div>;
}
