import { useState, useEffect } from "react";
import { Grid } from "antd";

const { useBreakpoint } = Grid;

export default function useScreenXS() {
    const [screenXS, setScreenXS] = useState(false);
    const screens = useBreakpoint();

    useEffect(() => {
        const screenWidths = Object.entries(screens).filter(screen => !!screen[1]);
        setScreenXS(screenWidths.length === 1 && screenWidths[0][0] === "xs");
    }, [screens]);

    return screenXS;
}
