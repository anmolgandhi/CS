class Popup extends React.Component {
  render() {
    return (
      React.createElement("div", { className: "popup" },
      React.createElement("div", { className: "popup_inner" },
      React.createElement("h1", null, this.props.text),
      React.createElement("button", { onClick: this.props.closePopup }, "close me"))));



  }}

class App extends React.Component {
  constructor() {
    super();
    this.state = {
      showPopup: false };

  }
  togglePopup() {
    this.setState({
      showPopup: !this.state.showPopup });

  }
  render() {
    return (
      React.createElement("div", { className: "app" },
      React.createElement("h1", null, "hihi"),
      React.createElement("button", { onClick: this.togglePopup.bind(this) }, "show popup"),
      React.createElement("button", {
        onClick: () => {
          alert("woooooooot?");
        } }, "try me when popup is open"),



      this.state.showPopup ?
      React.createElement(Popup, { text: "Close Me", closePopup: this.togglePopup.bind(this) }) :
      null));


  }}


ReactDOM.render(React.createElement(App, null), document.getElementById("content"));