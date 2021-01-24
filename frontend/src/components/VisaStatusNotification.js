import React from "react";
import Notification from "react-web-notification";
import { useWebSocketSubscribe } from "../hooks";

/** Use websocket hook in this empty JSX component instead of global App scope */
export default function VisaStatusNotification() {
    const [notificationTitle, notificationOption] = useWebSocketSubscribe();
    return <Notification title={notificationTitle} options={notificationOption} timeout={10000} />;
}
