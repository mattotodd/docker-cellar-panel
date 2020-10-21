import React from "react"
import Head from 'next/head';

import { Navbar, Nav, NavDropdown} from 'react-bootstrap';
import { Container } from "react-bootstrap";

const Header = () => {
	return (
		<>
			<Head>
				<title>Cellar Controller</title>
			</Head>
			<Navbar bg="light" expand="lg">
			  <Container>
			  <Navbar.Brand href="#home" style={{color:"#493a34"}}><img src="/Crop_Guy.jpg" height="40px" alt="" /> <span>&nbsp;&nbsp;</span><img src="/OPBC-Text-Logo.png" height="40px" alt="" /> <span>&nbsp;&nbsp;</span> <span>Cellar Panel</span></Navbar.Brand>
			  </Container>
			</Navbar>
		</>
	)
}

export default Header


			  // <Navbar.Toggle aria-controls="basic-navbar-nav" />
			  // <Navbar.Collapse id="basic-navbar-nav">
			  //   <Nav className="mr-auto">
			  //     <Nav.Link href="#home">Home</Nav.Link>
			  //     <Nav.Link href="#link">Link</Nav.Link>
			  //     <NavDropdown title="Dropdown" id="basic-nav-dropdown">
			  //       <NavDropdown.Item href="#action/3.1">Action</NavDropdown.Item>
			  //       <NavDropdown.Item href="#action/3.2">Another action</NavDropdown.Item>
			  //       <NavDropdown.Item href="#action/3.3">Something</NavDropdown.Item>
			  //       <NavDropdown.Divider />
			  //       <NavDropdown.Item href="#action/3.4">Separated link</NavDropdown.Item>
			  //     </NavDropdown>
			  //   </Nav>
			  // </Navbar.Collapse>
