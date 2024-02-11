export default function loadBokehJS() {
  return new Promise((resolve, reject) => {
    const existingScript = document.getElementById("bokeh-js");

    if (!existingScript) {
      const script = document.createElement("script");
      script.src = "https://cdn.bokeh.org/bokeh/release/bokeh-2.4.0.min.js";
      script.id = "bokeh-js";
      document.body.appendChild(script);

      script.onload = () => {
        console.log("BokehJS loaded");
        resolve();
      };

      script.onerror = () => {
        reject(new Error("Failed to load BokehJS"));
      };
    } else {
      resolve();
    }
  });
}
