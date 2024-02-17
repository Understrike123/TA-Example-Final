import Dashboard from "../components/dashboard";
import React, { useState, useEffect } from "react";
import { Axios } from "axios";
import styles from "../components/dashboard/dashboard.module.css";
import loadBokehJS from "../lib/loadBokeh";

const Index = () => {
  const SERVER_ADDRESS = "seismic_backend";
  const [selectedOption, setSelectedOption] = useState("gray");
  const [numberValues, setNumberValues] = useState(["435", "100", "10", "800"]);
  const [bokehPlot, setBokehPlot] = useState(null);
  const [bokehLoaded, setBokehLoaded] = useState(false);

  const handleDropdownChange = (event) => {
    setSelectedOption(event.target.value);
    sendDataToFlask();
  };

  const handleNumberInputChange = (event, index) => {
    const newNumberValues = [...numberValues];
    newNumberValues[index] = event.target.value;
    setNumberValues(newNumberValues);
  };

  const sendDataToFlask = async () => {
    //fungsi asyncronous untuk mengirimkan data dan menerima data dari server flask
    const formData = {
      colr: selectedOption,
      amp: numberValues[0],
      cmpinc: numberValues[1],
      textcanvas: numberValues[2],
      xlaborient: numberValues[3],
    };

    try {
      const response = await fetch("http://127.0.0.1:5000/seisview2d", {
        //menangkap server flask men-teransfer data

        method: "POST", //method POST digunakan karena mengirimkan data ke flask
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });
      const data = await response.json(); //respon dari server flask diterima dan dimasukkan ke dalam variabel data
      setBokehPlot(data);
      console.log(data);
    } catch (error) {
      console.error("Error:", error);
    }
  };

  useEffect(() => {
    sendDataToFlask();
  }, []); // Panggil sendDataToFlask saat halaman dimuat

  useEffect(() => {
    if (bokehPlot) {
      // Hapus plot Bokeh lama
      const plotContainer = document.getElementById("myplot");
      plotContainer.innerHTML = ""; // Menghapus semua konten di dalam elemen

      // Buat elemen div baru untuk menampilkan plot Bokeh baru
      const newPlotElement = document.createElement("div");
      newPlotElement.id = "bokehPlot"; // Mengatur id untuk elemen baru

      // Tambahkan elemen div baru ke dalam div yang sesuai
      plotContainer.appendChild(newPlotElement);

      // Embed plot Bokeh baru ke dalam elemen div yang baru dibuat
      Bokeh.embed.embed_item(bokehPlot, "bokehPlot");
    }
  }, [bokehPlot]);

  useEffect(() => {
    loadBokehJS()
      .then(() => setBokehLoaded(true))
      .catch((error) => console.error("Failed to load BokehJS:", error));
  }, []);

  // Fungsi untuk mengirim data ke server Flask saat tombol enter ditekan
  const handleKeyPress = (event) => {
    if (event.key === "Enter") {
      sendDataToFlask();
    }
  };

  return (
    <div>
      <Dashboard />
      <div className="container box-border mx-auto max-w-7xl py-6 sm:px-6 lg:px-8 font-sans">
        <div className={`${styles.panel1} grid grid-cols-2 gap-2 `}>
          <div className={styles.widget}>
            <div>
              <label htmlFor="dropdown">Select Color Scale:</label>
              <select
                id="dropdown"
                value={selectedOption}
                onChange={handleDropdownChange}
              >
                <option value="gray">Gray</option>
                <option value="RdGy">RdGy</option>
                <option value="BrBg">BrBg</option>
                <option value="coolwarm">Coolwarm</option>
                <option value="RdBu">RdBu</option>
                <option value="spectral">Spectral</option>
                <option value="fire">Fire</option>
                <option value="magma">Magma</option>
                <option value="seismic">Seismic</option>
                <option value="bwr">Bwr</option>
                <option value="jet">Jet</option>
              </select>
            </div>
            <div>
              <label htmlFor="number1">Amplitude:</label>
              <input
                type="number"
                id="number1"
                value={numberValues[0]}
                onChange={(event) => handleNumberInputChange(event, 0)}
                onKeyDown={handleKeyPress}
              />
            </div>
            <div>
              <label htmlFor="number2">CMP Inc.:</label>
              <input
                type="number"
                id="number2"
                value={numberValues[1]}
                onChange={(event) => handleNumberInputChange(event, 1)}
                onKeyDown={handleKeyPress}
              />
            </div>
            <div>
              <label htmlFor="number3">X-label Orientation:</label>
              <input
                type="number"
                id="number3"
                value={numberValues[2]}
                onChange={(event) => handleNumberInputChange(event, 2)}
                onKeyDown={handleKeyPress}
              />
            </div>
            <div>
              <label htmlFor="number4">Plot Height:</label>
              <input
                type="number"
                id="number4"
                value={numberValues[3]}
                onChange={(event) => handleNumberInputChange(event, 3)}
                onKeyDown={handleKeyPress}
              />
            </div>
          </div>
          <div id="myplot" className={styles.graphic}></div>
        </div>
      </div>
    </div>
  );
};

export default Index;
