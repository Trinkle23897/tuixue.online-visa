import React, { useMemo, useState } from "react";
import PropTypes from "prop-types";
import { useSelector } from "react-redux";
import { Row, Col, Button, Tooltip, Space, Collapse, Tag, Modal, List } from "antd";
import { MailOutlined, QqOutlined, EllipsisOutlined, PlusOutlined } from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { useScreenXS } from "../../hooks";
import { makeNewestVisaStatusSelector, makeQqTgInfoSelector } from "../../redux/selectors";
import { findEmbassyAttributeByCode } from "../../utils/USEmbassy";
import { getTimeFromUTC } from "../../utils/misc";
import { overviewAttrProps, newestOverviewProps, overviewProps } from "./overviewPropTypes";
import "./VisaStatusOverview.less";

const { Panel } = Collapse;

const QQTGSubsModal = ({ qqGroups, tgLink, isModalVisible, setIsModalVisible }) => {
    const { t } = useTranslation();
    const qqGroupsStr = qqGroups.map((content, index) => ({
        index,
        desc: `${t("QQTGModalContentQQ", { index: index + 1 })}${content}`,
    }));
    return (
        <Modal
            title={t("QQTGModalTitle")}
            visible={isModalVisible}
            onOk={() => setIsModalVisible(false)}
            onCancel={() => setIsModalVisible(false)}
        >
            <p>
                {t("QQTGModalContentTG")}
                <a href={tgLink} target="_blank" rel="noreferrer">
                    {tgLink}
                </a>
            </p>
            <p>{t("QQTGModalContentQQDesc")}</p>
            <List
                itemLayout="vertical"
                dataSource={qqGroupsStr}
                renderItem={s => (
                    <List.Item key={s.index}>
                        <p>{s.desc}</p>
                    </List.Item>
                )}
            />
        </Modal>
    );
};
QQTGSubsModal.propTypes = {
    qqGroups: PropTypes.arrayOf(PropTypes.string),
    tgLink: PropTypes.string,
    isModalVisible: PropTypes.bool.isRequired,
    setIsModalVisible: PropTypes.func.isRequired,
};

const ContentActions = ({ children, embassyCode, onEmailSubsClick, onAddtionClick }) => {
    const { t } = useTranslation();
    const embassyLst = useSelector(state => state.metadata.embassyLst);
    const region = findEmbassyAttributeByCode("region", embassyCode, embassyLst);
    const index = region === "DOMESTIC" ? "domestic" : "nonDomestic";
    const isVisaTypeF = useSelector(state => state.visastatusTab === "F");
    const qqTgInfoSelector = useMemo(() => makeQqTgInfoSelector(index), [index]);
    const [qqGroups, tgLink] = useSelector(state => qqTgInfoSelector(state));
    const [QQTGSubsModalVisible, setQQTGSubsModalVisible] = useState(false);
    return (
        <Space direction="horizontal">
            <Tooltip title={t("overviewEmailIcon")}>
                <Button icon={<MailOutlined />} shape="circle" onClick={() => onEmailSubsClick()} />
            </Tooltip>
            {isVisaTypeF && (
                <Tooltip title={t("overviewQQIcon")}>
                    <Button icon={<QqOutlined />} shape="circle" onClick={() => setQQTGSubsModalVisible(true)} />
                </Tooltip>
            )}
            <Tooltip title={t("overviewAddtionalIcon")}>
                <Button icon={<EllipsisOutlined rotate={90} />} shape="circle" onClick={() => onAddtionClick()} />
            </Tooltip>
            {isVisaTypeF && (
                <QQTGSubsModal
                    qqGroups={qqGroups}
                    tgLink={tgLink}
                    isModalVisible={QQTGSubsModalVisible}
                    setIsModalVisible={setQQTGSubsModalVisible}
                />
            )}
            {children}
        </Space>
    );
};
ContentActions.propTypes = {
    children: PropTypes.oneOfType([PropTypes.arrayOf(PropTypes.node), PropTypes.node]),
    embassyCode: PropTypes.string.isRequired,
    onEmailSubsClick: PropTypes.func.isRequired,
    onAddtionClick: PropTypes.func.isRequired,
};

const ContentBar = ({ embassyCode, earliestDate, latestDate, newest }) => {
    const [t] = useTranslation();
    const { writeTime, availableDate } = newest;
    return (
        <Row align="middle" className="ovreview-content-row" gutter={16}>
            <Col md={{ span: 3 }}>{t(embassyCode)}</Col>
            <Col md={{ span: 4 }}>
                <Tooltip title={t("overviewEarliest")}>{earliestDate.join("/")}</Tooltip>
            </Col>
            <Col md={{ span: 4 }}>
                <Tooltip title={t("overviewLatest")}>{latestDate.join("/")}</Tooltip>
            </Col>
            <Col md={{ span: 8 }}>
                <Tooltip title={t("overviewNewest")}>
                    <Row justify="center" align="middle">
                        <Col xs={{ span: 11 }} md={{ span: 9 }}>
                            {availableDate.join("/")}
                        </Col>
                        <Col xs={{ span: 13 }} md={{ span: 9 }}>
                            <Tag>{`${t("at")} ${
                                writeTime.length === 1 ? writeTime : getTimeFromUTC(writeTime).join(":")
                            }`}</Tag>
                        </Col>
                    </Row>
                </Tooltip>
            </Col>
            <Col md={{ span: 5 }}>
                <ContentActions embassyCode={embassyCode} onEmailSubsClick={() => {}} onAddtionClick={() => {}} />
            </Col>
        </Row>
    );
};
ContentBar.propTypes = { ...overviewAttrProps, ...newestOverviewProps };

const ContentCard = ({ embassyCode, earliestDate, latestDate, newest }) => {
    const { t } = useTranslation();
    const [cardDrop, setCardDrop] = useState(false);
    const { writeTime, availableDate } = newest;

    const DropdownControlBtn = () => (
        <Tooltip title="Open Detail">
            <Button
                icon={<PlusOutlined rotate={cardDrop ? 45 : 0} />}
                shape="circle"
                onClick={() => setCardDrop(!cardDrop)}
            />
        </Tooltip>
    );

    const BriefOverview = () => (
        <Row align="middle">
            <Col span={8}>{t(embassyCode)}</Col>
            <Col span={cardDrop ? 0 : 8}>{availableDate.join("/")}</Col>
            <Col span={cardDrop ? 16 : 8}>
                <Row justify="end" align="middle">
                    <Col>
                        {cardDrop ? (
                            <ContentActions
                                embassyCode={embassyCode}
                                onEmailSubsClick={() => {}}
                                onAddtionClick={() => {}}
                            >
                                <DropdownControlBtn />
                            </ContentActions>
                        ) : (
                            <DropdownControlBtn />
                        )}
                    </Col>
                </Row>
            </Col>
        </Row>
    );

    return (
        <Collapse activeKey={cardDrop ? [embassyCode] : []} className="overview-dropdown-card" ghost>
            <Panel key={embassyCode} header={<BriefOverview />} showArrow={false} forceRender>
                <Row>
                    <Col span={8}>
                        <strong>{t("overviewEarliestDate")}: </strong>
                    </Col>
                    <Col span={8} className="content-data">
                        {earliestDate.join("/")}
                    </Col>
                    <Col span={8} />
                    <Col span={8}>
                        <strong>{t("overviewLatestDate")}: </strong>
                    </Col>
                    <Col span={8} className="content-data">
                        {latestDate.join("/")}
                    </Col>
                    <Col span={8} />
                    <Col span={8}>
                        <strong>{t("overviewNewestFetch")}: </strong>
                    </Col>
                    <Col span={16} className="content-data">
                        <Row justify="center" align="middle">
                            <Col span={12}>{availableDate.join("/")}</Col>
                            <Col span={12}>
                                <Tag>{`${t("at")} ${
                                    writeTime.length === 1 ? writeTime : getTimeFromUTC(writeTime).join(":")
                                }`}</Tag>
                            </Col>
                        </Row>
                    </Col>
                </Row>
            </Panel>
        </Collapse>
    );
};
ContentCard.propTypes = { ...overviewAttrProps, ...newestOverviewProps };

const HeaderBar = () => {
    const [t] = useTranslation();
    return (
        <Row align="middle" className="ovreview-header bar" gutter={16}>
            <Col xs={{ span: 0 }} md={{ span: 3 }}>
                <strong>{t("Location")}</strong>
            </Col>
            <Col xs={{ span: 0 }} md={{ span: 4 }}>
                <strong>{t("overviewEarliestDate")}</strong>
            </Col>
            <Col xs={{ span: 0 }} md={{ span: 4 }}>
                <strong>{t("overviewLatestDate")}</strong>
            </Col>
            <Col xs={{ span: 0 }} md={{ span: 8 }}>
                <strong>{t("overviewNewestFetch")}</strong>
            </Col>
            <Col xs={{ span: 0 }} md={{ span: 5 }}>
                <strong>{t("overviewActions")}</strong>
            </Col>
        </Row>
    );
};

const HeaderCard = () => {
    const [t] = useTranslation();
    return (
        <Row align="middle" className="ovreview-header card">
            <Col span={8}>
                <strong>{t("Location")}</strong>
            </Col>
            <Col span={8}>
                <strong>{t("overviewNewestFetch")}</strong>
            </Col>
            <Col span={8}>
                <strong>{t("overviewActions")}</strong>
            </Col>
        </Row>
    );
};

export const OverviewHeader = () => {
    const screenXS = useScreenXS();
    return screenXS ? <HeaderCard /> : <HeaderBar />;
};

export const OverviewContent = ({ overview }) => {
    const screenXS = useScreenXS();
    const newestVisaStatueSelector = useMemo(
        () => makeNewestVisaStatusSelector(overview.visaType, overview.embassyCode),
        [overview],
    );
    const newestVisaStatus = useSelector(state => newestVisaStatueSelector(state));
    const newest = newestVisaStatus || { writeTime: "/", availableDate: ["/"] };

    return screenXS ? <ContentCard {...overview} newest={newest} /> : <ContentBar {...overview} newest={newest} />;
};
OverviewContent.propTypes = overviewProps;
