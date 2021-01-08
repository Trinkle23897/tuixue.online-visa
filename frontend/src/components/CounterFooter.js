import React from "react";
import { useTranslation } from "react-i18next";

export default function CounterFooter() {
    const [t] = useTranslation();
    return (
        <p style={{ textAlign: "center" }}>
            {t("counterFooterP1")}
            <span id="busuanzi_value_page_pv" />
            {t("counterFooterP2")}
        </p>
    );
}
