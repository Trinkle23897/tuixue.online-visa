import React from "react";
import { useWebSocketSubscribe } from "../hooks";

/** Use websocket hook in this empty JSX component instead of global App scope */
export default function VisaStatusNotification() {
    useWebSocketSubscribe();
    return <></>;
}
