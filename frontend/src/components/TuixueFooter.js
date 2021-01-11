import React, { useState } from "react";
import { Divider, Tabs, Image } from "antd";
import { useTranslation } from "react-i18next";
import { DiscussionEmbed } from "disqus-react";
import ReactMarkdown from "react-markdown";
import { useScreenXS } from "../hooks";
import payCode from "../assets/img/pay.png";
import "./TuixueFooter.less";

const { TabPane } = Tabs;

export default function TuixueFooter() {
    const [t] = useTranslation();
    const screenXS = useScreenXS();
    const [disqusType, setDisqusType] = useState("visa");
    return (
        <>
            <Divider />
            <ReactMarkdown>{t("footer.prjDesc")}</ReactMarkdown>
            <div className="tuixue-footer">
                <Image src={payCode} alt="payCode" width={screenXS ? "100%" : "60%"} />
            </div>
            <Divider dashed />
            <p className="tuixue-footer">
                {t("footer.part1")}
                <span id="busuanzi_value_page_pv" />
                {t("footer.part2")}
                <a href="https://www.zhihu.com/question/318624725/answer/875527594">{t("footer.part3")}</a>
            </p>
            <Tabs centered activeKey={disqusType} onChange={activeKey => setDisqusType(activeKey)}>
                <TabPane tab={t("disqus.domestic")} key="visa" />
                <TabPane tab={t("disqus.global")} key="global" />
            </Tabs>
            <DiscussionEmbed
                shortname="tuixue-online"
                config={{
                    url: `https://tuixue.online/${disqusType}/`,
                    identifier: disqusType === "visa" ? "tuixue-online" : "global",
                    title: "tuixue-online",
                }}
            >
                {t("disqus.loadFail")}
            </DiscussionEmbed>
        </>
    );
}
