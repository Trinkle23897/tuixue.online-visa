import React, { useEffect, useState } from "react";
import Notification from "react-web-notification";
import { useWebSocketSubscribe } from "../hooks";

/** Use websocket hook in this empty JSX component instead of global App scope */
export default function VisaStatusNotification() {
    const [notificationTitle, notificationOption] = useWebSocketSubscribe();
    const [swReg, setSwReg] = useState(null);
    useEffect(() => {
        navigator.serviceWorker.register("/sw.js").then(reg => {
            if ("showNotification" in reg) {
                setSwReg(reg);
            }
        });
    });
    return (
        <Notification title={notificationTitle} options={notificationOption} timeout={10000} swRegistration={swReg} />
    );
}
