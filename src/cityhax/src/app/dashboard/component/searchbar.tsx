import React, { useState } from 'react';

interface SearchBarProps {
  onSearch: (term: string) => void;
}

const SearchBar: React.FC<SearchBarProps> = ({ onSearch }) => {
  const [searchTerm, setSearchTerm] = useState<string>('');

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    onSearch(searchTerm);
    event.preventDefault();
  };

  return (
    <div className="search-bar">
      <form onSubmit={handleSubmit}> {/* Use onSubmit with the function */}
        <input
          type="text"
          value={searchTerm}
          onChange={handleInputChange}
          placeholder="Enter School District: "
        />
      </form>
    </div>
  );
};

export default SearchBar;
