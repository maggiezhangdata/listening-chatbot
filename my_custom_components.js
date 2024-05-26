import { Streamlit, withStreamlitConnection } from "streamlit-component-lib";
import React, { useEffect } from "react";

const URLComponent = (props) => {
  const handleClick = (url) => {
    // This sends the clicked URL back to Streamlit
    Streamlit.setComponentValue(url);
  };

  return (
    <div>
      {props.urls.map((url, index) => (
        <a key={index} href={url} onClick={() => handleClick(url)} target="_blank" rel="noopener noreferrer">
          {url}
        </a>
      ))}
    </div>
  );
}

export default withStreamlitConnection(URLComponent);
