import { useEffect, useRef, useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { updateNewest } from "../redux/visastatusNewest";
import { openLatestVisaStatusSocket } from "../services";
import { renameObjectKeys } from "../utils/misc";

const ONE_MINUTE = 60 * 1000;

export default function useWebSocketSubscribe() {
    const dispatch = useDispatch();
    const visastatusFilter = useSelector(state => state.visastatusFilter);
    const [wsConnected, setWsConnected] = useState(false);
    const webSocketRef = useRef(openLatestVisaStatusSocket());

    // This effect SHOULD keep web socket alive and reconnect when it's closed
    useEffect(() => {
        if (!wsConnected) {
            if (webSocketRef.current.readyState === WebSocket.CLOSED) {
                webSocketRef.current = openLatestVisaStatusSocket();
            }
        }

        webSocketRef.current.onopen = () => setWsConnected(true);
        webSocketRef.current.onclose = () => setWsConnected(false);
        webSocketRef.current.onerror = e => console.log(e);
        webSocketRef.current.onmessage = e => {
            const newestVisaStatus = renameObjectKeys(JSON.parse(e.data));
            if (newestVisaStatus.length > 0) {
                const { visaType } = newestVisaStatus[0];
                dispatch(updateNewest({ visaType, current: newestVisaStatus }));
            }
        };
    }, [wsConnected, dispatch]);

    useEffect(() => {
        // We don't need to check wsConnect here because WebSocket.readyState must be OPEN to
        // send a message.
        const getNewestVisaStatus = visaType =>
            webSocketRef.current.readyState === WebSocket.OPEN &&
            webSocketRef.current.send(JSON.stringify([visaType, visastatusFilter[visaType]]));

        Array.from("FBOHL").forEach(visaType => getNewestVisaStatus(visaType));

        const intervalIds = Array.from("FBOHL").map(visaType =>
            setInterval(() => getNewestVisaStatus(visaType), ONE_MINUTE),
        );
        return () => intervalIds.forEach(intvId => clearInterval(intvId));
    }, [wsConnected, visastatusFilter]);
}
