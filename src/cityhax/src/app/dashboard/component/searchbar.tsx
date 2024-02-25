import React, { useState } from 'react';

interface SearchBarProps {
  // Add any additional props you might need
}

const SearchBar: React.FC<SearchBarProps> = () => {
  const [searchTerm, setSearchTerm] = useState<string>('');

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    console.log(`Form Submitted\nSearch Term: ${searchTerm}`);
    event.preventDefault();
  };

  return (
    <div className="search-bar">
      <form onSubmit={handleSubmit}> {/* Use onSubmit with the function */}
        <input
          type="text"
          value={searchTerm}
          onChange={handleInputChange}
          placeholder="Please enter postal code: "
        />
      </form>
    </div>
  );
};

export default SearchBar;
