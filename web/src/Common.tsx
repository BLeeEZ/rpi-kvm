import React from 'react';
import { Container, Row, Col } from 'react-bootstrap';

export const ServerConfig = {
  url: "/",
  name: "",
  port: 8080,
}

export type BannerProps = {
  message: string;
};

export class InfoBanner extends React.Component<BannerProps, any> {
  render() {
    return (
      <div className="alert alert-primary" role="alert">
        {this.props.message}
      </div>
    );
  }
}

export class SuccessBanner extends React.Component<BannerProps, any> {
  render() {
    return (
      <div className="alert alert-success" role="alert">
        {this.props.message}
      </div>
    );
  }
}

export class ErrorAlert extends React.Component<BannerProps, any> {
  render() {
    return (
      <div className="alert alert-danger" role="alert">
        {this.props.message}
      </div>
    );
  }
}

export type WelcomeBannerProps = {
  name: string;
  message: string;
};

export class WelcomeBanner extends React.Component<WelcomeBannerProps, any> {
  render() {
    return (
      <Container className="py-3 text-center">
        <Row className="py-lg-5">
          <Col lg={6} md={8} className="mx-auto">
            <h1 className="fw-light">{this.props.name}</h1>
            <p className="lead text-muted">{this.props.message}</p>
          </Col>
        </Row>
      </Container>
    );
  }
}

export class LoadingSpinner extends React.Component {
  render() {
    return (
      <div className="d-flex justify-content-center">
        <div className="spinner-border text-secondary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }
}
