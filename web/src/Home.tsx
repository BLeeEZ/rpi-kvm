import React from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import { WelcomeBanner } from './Common';

export default function Home() {
  return (
    <>
      <Container>
        <Row className="py-5">
          <Col>
            <WelcomeBanner name="Raspberry Pi K(V)M" message="Manage your connected bluetooth clients" />
          </Col>
        </Row>
      </Container>
    </>
  );
}
