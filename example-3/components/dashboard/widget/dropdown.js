import { useState } from "react";

const Dropdown = ({ option, onSelect }) => {
  const [selectOption, setSelectOption] = useState(null);

  const handleSelect = (option) => {
    setSelectOption(option);
    onSelect(option);
  };

  return (
    <div>
      <label>color</label>
      <br></br>
      <select
        onChange={(e) => handleSelect(e.target.value)}
        value={selectOption}
        className="w-full px-4 py-2 rounded-md border border-white bg-white text-blue-500 focus:outline-none focus:border-blue-300"
      >
        {option.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {selectOption && <p>Anda memilih: {selectOption}</p>}
    </div>
  );
};

export default Dropdown;
