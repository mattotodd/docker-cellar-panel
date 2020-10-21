import 'bootstrap/dist/css/bootstrap.min.css';
import Header from '../layouts/header';

function MyApp({ Component, pageProps }) {
	const pagestyle = {
	  color: "white",
	  backgroundColor: "#676767",
	  fontFamily: "Futura,Trebuchet MS,Arial,sans-serif"
	};
  return (
  	<div style={pagestyle}> 
  		<Header />
  		<Component style={pagestyle} {...pageProps} />
  	</div>
  )
}

export default MyApp