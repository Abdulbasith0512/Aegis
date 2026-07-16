import React, { useState, useEffect } from 'react';
import { Search, SlidersHorizontal, X } from 'lucide-react';

export interface FilterOption {
  key: string;
  label: string;
  options: { value: string; label: string }[];
}

interface FilterBarProps {
  searchPlaceholder?: string;
  searchValue: string;
  onSearchChange: (value: string) => void;
  filters?: FilterOption[];
  activeFilters?: Record<string, string[]>;
  onFilterChange?: (key: string, values: string[]) => void;
  onClearAll?: () => void;
  totalCount?: number;
  filteredCount?: number;
}

export const FilterBar: React.FC<FilterBarProps> = ({
  searchPlaceholder = 'Search…',
  searchValue,
  onSearchChange,
  filters = [],
  activeFilters = {},
  onFilterChange,
  onClearAll,
  totalCount,
  filteredCount,
}) => {
  const hasActiveFilters = Object.values(activeFilters).some((v) => v.length > 0) || searchValue;

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 8,
        flexWrap: 'wrap',
        marginBottom: 12,
      }}
    >
      {/* Search */}
      <div style={{ position: 'relative', minWidth: 220, flex: 1, maxWidth: 360 }}>
        <Search
          size={13}
          style={{
            position: 'absolute',
            left: 9,
            top: '50%',
            transform: 'translateY(-50%)',
            color: 'var(--gray-500)',
            pointerEvents: 'none',
          }}
        />
        <input
          className="input"
          style={{ paddingLeft: 30 }}
          placeholder={searchPlaceholder}
          value={searchValue}
          onChange={(e) => onSearchChange(e.target.value)}
        />
        {searchValue && (
          <button
            onClick={() => onSearchChange('')}
            style={{
              position: 'absolute',
              right: 8,
              top: '50%',
              transform: 'translateY(-50%)',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              color: 'var(--gray-500)',
              padding: 2,
              display: 'flex',
            }}
          >
            <X size={11} />
          </button>
        )}
      </div>

      {/* Filter dropdowns */}
      {filters.map((filter) => (
        <FilterDropdown
          key={filter.key}
          filter={filter}
          selected={activeFilters[filter.key] || []}
          onChange={(vals) => onFilterChange?.(filter.key, vals)}
        />
      ))}

      {/* Clear all */}
      {hasActiveFilters && onClearAll && (
        <button className="btn btn-ghost" onClick={onClearAll} style={{ color: 'var(--risk-critical-text)', fontSize: 'var(--text-12)' }}>
          <X size={12} /> Clear all
        </button>
      )}

      {/* Count */}
      {totalCount !== undefined && (
        <div
          style={{
            marginLeft: 'auto',
            fontSize: 'var(--text-12)',
            color: 'var(--gray-500)',
            fontFamily: 'var(--font-mono)',
            whiteSpace: 'nowrap',
          }}
        >
          {filteredCount !== undefined && filteredCount !== totalCount
            ? `${filteredCount.toLocaleString()} / ${totalCount.toLocaleString()}`
            : `${totalCount.toLocaleString()} rows`}
        </div>
      )}
    </div>
  );
};

interface FilterDropdownProps {
  filter: FilterOption;
  selected: string[];
  onChange: (vals: string[]) => void;
}

const FilterDropdown: React.FC<FilterDropdownProps> = ({ filter, selected, onChange }) => {
  const [open, setOpen] = useState(false);
  const hasSelection = selected.length > 0;

  const toggle = (value: string) => {
    if (selected.includes(value)) {
      onChange(selected.filter((v) => v !== value));
    } else {
      onChange([...selected, value]);
    }
  };

  return (
    <div style={{ position: 'relative' }}>
      <button
        className="btn btn-outline"
        onClick={() => setOpen((o) => !o)}
        style={{
          borderColor: hasSelection ? 'var(--accent-muted)' : undefined,
          color: hasSelection ? 'var(--accent)' : undefined,
        }}
      >
        <SlidersHorizontal size={12} />
        {filter.label}
        {hasSelection && (
          <span
            style={{
              background: 'var(--accent-dim)',
              color: 'var(--accent)',
              borderRadius: 9999,
              padding: '0 5px',
              fontSize: 'var(--text-11)',
              fontWeight: 700,
              fontFamily: 'var(--font-mono)',
            }}
          >
            {selected.length}
          </span>
        )}
      </button>
      {open && (
        <>
          <div
            style={{ position: 'fixed', inset: 0, zIndex: 10 }}
            onClick={() => setOpen(false)}
          />
          <div
            style={{
              position: 'absolute',
              top: 'calc(100% + 6px)',
              left: 0,
              background: 'var(--surface-3)',
              border: '1px solid var(--border-2)',
              borderRadius: 'var(--radius-md)',
              overflow: 'hidden',
              zIndex: 20,
              minWidth: 160,
              boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
            }}
          >
            {filter.options.map((opt) => (
              <label
                key={opt.value}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  padding: '7px 12px',
                  cursor: 'pointer',
                  fontSize: 'var(--text-13)',
                  color: 'var(--gray-200)',
                  background: selected.includes(opt.value) ? 'var(--surface-4)' : 'transparent',
                }}
              >
                <input
                  type="checkbox"
                  checked={selected.includes(opt.value)}
                  onChange={() => toggle(opt.value)}
                  style={{ accentColor: 'var(--accent)' }}
                />
                {opt.label}
              </label>
            ))}
          </div>
        </>
      )}
    </div>
  );
};
