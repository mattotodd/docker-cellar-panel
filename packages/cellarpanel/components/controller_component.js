import React, { useState } from "react"
import Router from 'next/router';
import { Container, Row, Col, Modal, Button, Spinner } from "react-bootstrap";
import { Knob } from "react-rotary-knob";

import s12 from './knob_skins/s12'
import s8 from './knob_skins/s8'


import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import {
  faArrowRight,
  faBan,
  faBeer, 
  faChevronCircleRight,
  faCalendarDay, 
  faGlassWhiskey, 
  faFlask 
} from '@fortawesome/free-solid-svg-icons'

import {
  faArrowAltCircleRight, 
} from '@fortawesome/free-regular-svg-icons'


function BatchInfo(props) {
  const batch = props.batch;
  return (
    <>
    <Col xs={12}>
      <Row>
        <Col xs={8}><FontAwesomeIcon icon={faBeer} /> <span>&nbsp;</span>{batch.Beer} - #{batch['Batch #']}</Col>
        <Col xs={4} md={4} style={{textAlign:'right'}}><span>&nbsp;</span>{batch['Batch Size']}</Col>
        <Col xs={8} md={8}><FontAwesomeIcon icon={faCalendarDay} /> <span>&nbsp;</span>Brewed: {batch['Date Brewed']} ({batch['Days in Vessel']})</Col>
        <Col xs={4} md={4} style={{textAlign:'right'}}>OG: {batch['OG']}</Col>
        <Col xs={7} md={7}><FontAwesomeIcon icon={faGlassWhiskey} /> <span>&nbsp;</span>Volume: {batch['Actual Volume']} bbl</Col>
        <Col xs={5} md={5} style={{textAlign:'right'}}>FG: {batch['FG']}</Col>
      </Row>
    </Col>
    <Col><hr style={{borderWidth: '4px', borderColor: '#454545', marginBottom: '30px'}} /></Col>
    </>
  );
}


class ControllerComponent extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      nextSetPoint: this.props.control.temp, 
      adjustingSetPoint: false,
      confirmChange: false,
      savingSetPoint: false
    };
  }

  changeSetpointValue = (val) => {
   this.setState({
      nextSetPoint: parseInt(val, 10)
    });
  }

  setPointDragStart = (val) => {
    this.setState({
      adjustingSetPoint: true
    });
    this.dragStart = new Date();
  }

  setPointDragEnd = (val) => {
    const dragEnd = new Date();
    if (Math.abs(dragEnd.getTime() - this.dragStart.getTime()) < 1000 ) {
      // skip quick drags
      this.setState({
        adjustingSetPoint: false
      });
      return;
    }
    if (this.state.nextSetPoint && this.state.nextSetPoint != this.props.control.set_point) {
      this.setState({
        confirmChange: true
      });
    }
  }

  closeConfirm = () => {
    this.setState({
      confirmChange: false,
      adjustingSetPoint: false
    });
  }

  doSetPointChange = () => {
    this.setState({ savingSetPoint: true });
    const Opr = 3;
    const Adr = this.props.control.address;
    const Ty = 2;
    const oVal = parseInt(this.state.nextSetPoint * 10);
    const param = new Date().getTime() + "o" + Opr + "a" + Adr + "t" + Ty + "v" + oVal;

    const update_url = `/api/set_control`;

    fetch(`/api/set_control`, {
      method: 'POST',
      body: JSON.stringify({param})
    }).then((set_resp) => {
      setTimeout(() => this.props.reloadData(), 100);
      setTimeout(() => {
        this.setState({
          confirmChange: false,
          adjustingSetPoint: false,
          savingSetPoint: false
        });
      }, 3000);
    });
  }

  render () {
    return (
      <>
        <Col sm={12} md={6} lg={4}>
        <Row>
          <Col xs={6} sm={8} md={6}>
            <h1>{this.props.control.label}</h1>
            <p>
              Temp: {this.props.control.temp}&deg;F<br />
              Setpoint: {this.props.control.set_point}&deg;F<br />
              Valve: {(this.props.control.valve_open == '1') ? <FontAwesomeIcon icon={faArrowAltCircleRight} title="Open" /> : <FontAwesomeIcon icon={faBan} title="Closed" />}<br />
            </p>
            <hr style={{borderColor: '#454545'}} />
          </Col>
          <Col xs={6} sm={4} md={6}>
            <Knob 
              style={{
                width: "100%",
                height: "100%",
                display: "inline-block"
              }} 
              onStart={this.setPointDragStart}
              onEnd={this.setPointDragEnd}
              onChange={this.changeSetpointValue} 
              rotateDegrees={235} 
              clampMax={270} 
              min={34} max={100} 
              unlockDistance={50} 
              value={(this.state.adjustingSetPoint) ? this.state.nextSetPoint : this.props.control.temp} 
              skin={s12} />
          </Col>
          {this.props.control.batch_info['Batch #'] != 0 &&
            <BatchInfo batch={this.props.control.batch_info}  / >
          }
        </Row>
        </Col>

        <Modal show={this.state.confirmChange} onHide={this.closeConfirm}>
          <Modal.Header closeButton>
            <Modal.Title>Change <strong>{this.props.control.label}</strong> set point?</Modal.Title>
          </Modal.Header>
          <Modal.Body>Are you sure you want to change the setpoint to {this.state.nextSetPoint}&deg;F</Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={this.closeConfirm}>
              Cancel
            </Button>
            {!this.state.savingSetPoint &&
              <Button variant="danger" onClick={this.doSetPointChange}>
                Set to {this.state.nextSetPoint}&deg;F
              </Button>}
            {this.state.savingSetPoint &&
              <Button variant="primary" disabled>
                <Spinner
                  as="span"
                  animation="border"
                  size="sm"
                  role="status"
                  aria-hidden="true"
                />
                <span>&nbsp;</span>Setting...
              </Button> }
          </Modal.Footer>
        </Modal>
      </>
    )
  }
}

export default ControllerComponent
