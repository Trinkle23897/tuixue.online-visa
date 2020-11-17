import React, { useEffect, useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { InfoCircleFilled } from "@ant-design/icons";
import { notification } from "antd";

export default function NotificationPopUp() {
    const dispatch = useDispatch();

    useEffect(() => {
        // notification.open({
        //     message: "New Avaialbe Visa Appointment!",
        //     description: `Current latest written: ${JSON.stringify(latestWrittenData)}`,
        //     duration: 1.5,
        //     icon: <InfoCircleFilled size="large" />,
        // });
    });

    return <></>;
}
