import React, { useState } from "react";
import PropTypes from "prop-types";
import { HashLink as Link } from "react-router-hash-link";
import { Row, Col, Button, Layout, Menu, Typography, Popover } from "antd";
import { MenuOutlined, CloseOutlined } from "@ant-design/icons";
import "./TuixueHeader.less";

const { Header } = Layout;
const { Title } = Typography;

const Logo = () => (
    <Col xs={{ span: 12 }} lg={{ span: 4, push: 1 }} className="logo">
        <img src="https://via.placeholder.com/40" alt="tuixue logo" />
        <Title>Tuixue</Title>
    </Col>
);

const NavMenu = ({ mode, theme, onClick }) => {
    return (
        <Menu theme={theme} mode={mode} onClick={onClick ? () => onClick() : () => {}}>
            <Menu.Item key="visastatus">
                {/* <Link to="/" component={Typography.Text}> */}
                Visa Status
                {/* </Link> */}
            </Menu.Item>
            <Menu.Item key="placeholder">Item 1</Menu.Item>
        </Menu>
    );
};
NavMenu.propTypes = {
    mode: PropTypes.oneOf(["vertical", "horizontal", "inline"]),
    theme: PropTypes.oneOf(["dark", "light"]),
    onClick: PropTypes.func,
};

const NavMenuPopover = () => {
    const [menuPop, setMenuPop] = useState(false);

    return (
        <Popover
            content={<NavMenu mode="vertical" theme="light" onClick={() => setMenuPop(!menuPop)} />}
            visible={menuPop}
            overlayStyle={{ minWidth: "65vw" }}
            trigger="click"
            placement="bottomRight"
            arrowPointAtCenter
        >
            <Button
                onClick={() => setMenuPop(!menuPop)}
                size="large"
                icon={menuPop ? <CloseOutlined /> : <MenuOutlined />}
                ghost
            />
        </Popover>
    );
};

export default function Nav() {
    return (
        <Header className="tuixue-header">
            <Row gutter={{ xs: 16, lg: 32 }}>
                <Logo />
                <Col xs={{ span: 0 }} lg={{ span: 6, push: 1 }}>
                    <NavMenu mode="horizontal" theme="dark" />
                </Col>
                <Col xs={{ span: 4, push: 8 }} lg={{ span: 0 }}>
                    <NavMenuPopover />
                </Col>
            </Row>
        </Header>
    );
}
