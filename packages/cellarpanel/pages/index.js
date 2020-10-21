import React from "react"
import { Container, Row, Col } from "react-bootstrap";
import { Knob } from "react-rotary-knob";

import { getPanelInfo } from "../utils/cellar-helper";
import ControllerComponent from "../components/controller_component";

async function fetchData(ctx) {
  let host = (ctx && ctx.req) ? `http://cellar-webapp:3000` : '';
  console.log(host);
  const response = await fetch(`${host}/api/get_panel_info`);
  const panelInfo = await response.json();

  return { panelInfo };
}

class IndexPage extends React.Component {
  constructor(props) {
    super(props);
    this.state = {loading: false, panelInfo: props.panelInfo};
  }

  componentDidMount() {
    setInterval(() => this.reloadData(), 60000);
  }

  reloadData = () => {
    fetchData().then((updatedData) => {
      this.setState(updatedData);;
    });
  }

  render () {
    const readAt = new Date(Date.parse(this.state.panelInfo.read_at+"Z"))
    const time_str = readAt.toLocaleTimeString();
    const date_str = readAt.toDateString()
    return (
      <Container>
        <Row>
          <Col>
              <p style={{textAlign: 'right', color: '#282828', fontSize: '.8em'}}>Recorded: {date_str} {time_str}</p>
          </Col>
        </Row>
        <Row>
          { this.state.panelInfo.controls.map((control) => {
            return <ControllerComponent key={control.address} control={control} readAt={this.state.panelInfo.read_at} reloadData={this.reloadData} />
          })}
        </Row>
      </Container>
    )
  }
}

IndexPage.getInitialProps = fetchData;
export default IndexPage
