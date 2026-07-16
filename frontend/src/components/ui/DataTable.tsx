import React, { useState, useMemo, useCallback } from 'react';
import { ChevronUp, ChevronDown, ChevronsUpDown, ChevronLeft, ChevronRight } from 'lucide-react';

export type SortDirection = 'asc' | 'desc' | null;

export interface ColumnDef<T> {
  key: keyof T | string;
  header: string;
  width?: number | string;
  minWidth?: number;
  sortable?: boolean;
  mono?: boolean;
  render?: (value: unknown, row: T, rowIndex: number) => React.ReactNode;
}

interface DataTableProps<T> {
  columns: ColumnDef<T>[];
  data: T[];
  rowKey: (row: T) => string;
  maxHeight?: number;
  newRowIds?: Set<string>;
  onRowClick?: (row: T) => void;
  emptyMessage?: string;
  loading?: boolean;
  /** Rows per page. Set to 0 or undefined to show all (not recommended for >200 rows). */
  pageSize?: number;
}

function getNestedValue<T>(obj: T, key: string): unknown {
  return key.split('.').reduce<unknown>((acc, k) => {
    if (acc && typeof acc === 'object') {
      return (acc as Record<string, unknown>)[k];
    }
    return undefined;
  }, obj);
}

/**
 * Paginated, sortable data table with sticky header, new-row flash animation,
 * and row hover highlights. Defaults to 50 rows per page for performance.
 */
export function DataTable<T>({
  columns,
  data,
  rowKey,
  maxHeight = 520,
  newRowIds,
  onRowClick,
  emptyMessage = 'No data',
  loading = false,
  pageSize = 50,
}: DataTableProps<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDir, setSortDir] = useState<SortDirection>(null);
  const [page, setPage] = useState(0);

  // Reset to page 0 when data changes (e.g., filter or flush)
  const dataFingerprint = data.length;
  const [prevFingerprint, setPrevFingerprint] = useState(dataFingerprint);
  if (dataFingerprint !== prevFingerprint) {
    setPage(0);
    setPrevFingerprint(dataFingerprint);
  }

  const handleSort = useCallback((key: string) => {
    setSortKey(prev => {
      if (prev !== key) {
        setSortDir('asc');
        return key;
      }
      setSortDir(dir => {
        if (dir === 'asc') return 'desc';
        setSortKey(null);
        return null;
      });
      return prev;
    });
  }, []);

  const sorted = useMemo(() => {
    if (!sortKey || !sortDir) return data;
    return [...data].sort((a, b) => {
      const av = getNestedValue(a, sortKey);
      const bv = getNestedValue(b, sortKey);
      if (av === bv) return 0;
      if (av == null) return 1;
      if (bv == null) return -1;
      const cmp = av < bv ? -1 : 1;
      return sortDir === 'asc' ? cmp : -cmp;
    });
  }, [data, sortKey, sortDir]);

  // Pagination
  const usePagination = pageSize > 0 && sorted.length > pageSize;
  const totalPages = usePagination ? Math.ceil(sorted.length / pageSize) : 1;
  const pageRows = usePagination ? sorted.slice(page * pageSize, (page + 1) * pageSize) : sorted;

  if (loading) {
    return (
      <div style={{ padding: 24 }}>
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="skeleton" style={{ height: 32, marginBottom: 6 }} />
        ))}
      </div>
    );
  }

  return (
    <div>
      <div style={{ overflowX: 'auto', overflowY: 'auto', maxHeight, position: 'relative' }}>
        <table
          style={{
            width: '100%',
            borderCollapse: 'collapse',
            fontSize: 'var(--text-13)',
          }}
        >
          <thead>
            <tr
              style={{
                position: 'sticky',
                top: 0,
                zIndex: 2,
                background: 'var(--surface-1)',
              }}
            >
              {columns.map((col) => {
                const key = col.key as string;
                const isSorted = sortKey === key;
                return (
                  <th
                    key={key}
                    style={{
                      padding: '7px 12px',
                      textAlign: 'left',
                      fontSize: 'var(--text-11)',
                      fontWeight: 600,
                      letterSpacing: '0.05em',
                      textTransform: 'uppercase',
                      color: isSorted ? 'var(--accent)' : 'var(--gray-500)',
                      borderBottom: '1px solid var(--border-1)',
                      whiteSpace: 'nowrap',
                      cursor: col.sortable ? 'pointer' : 'default',
                      userSelect: 'none',
                      width: col.width,
                      minWidth: col.minWidth,
                    }}
                    onClick={() => col.sortable && handleSort(key)}
                  >
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                      {col.header}
                      {col.sortable && (
                        isSorted ? (
                          sortDir === 'asc' ? <ChevronUp size={11} /> : <ChevronDown size={11} />
                        ) : (
                          <ChevronsUpDown size={11} style={{ opacity: 0.4 }} />
                        )
                      )}
                    </span>
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody>
            {pageRows.length === 0 ? (
              <tr>
                <td
                  colSpan={columns.length}
                  style={{
                    padding: '48px 24px',
                    textAlign: 'center',
                    color: 'var(--gray-500)',
                    fontSize: 'var(--text-14)',
                  }}
                >
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              pageRows.map((row, rowIdx) => {
                const id = rowKey(row);
                const isNew = newRowIds?.has(id);
                return (
                  <tr
                    key={id}
                    className={isNew ? 'row-flash' : ''}
                    onClick={() => onRowClick?.(row)}
                    style={{
                      borderBottom: '1px solid var(--border-0)',
                      cursor: onRowClick ? 'pointer' : 'default',
                      transition: 'background var(--motion-fast)',
                    }}
                    onMouseEnter={(e) => {
                      (e.currentTarget as HTMLTableRowElement).style.background = 'var(--surface-3)';
                    }}
                    onMouseLeave={(e) => {
                      (e.currentTarget as HTMLTableRowElement).style.background = '';
                    }}
                  >
                    {columns.map((col) => {
                      const key = col.key as string;
                      const rawValue = getNestedValue(row, key);
                      const content = col.render ? col.render(rawValue, row, rowIdx) : String(rawValue ?? '—');
                      return (
                        <td
                          key={key}
                          style={{
                            padding: '7px 12px',
                            color: 'var(--gray-200)',
                            whiteSpace: 'nowrap',
                            fontFamily: col.mono ? 'var(--font-mono)' : 'var(--font-sans)',
                            fontSize: col.mono ? 'var(--text-12)' : 'var(--text-13)',
                          }}
                        >
                          {content}
                        </td>
                      );
                    })}
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination controls */}
      {usePagination && (
        <div
          style={{
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            padding: '8px 14px',
            borderTop: '1px solid var(--border-0)',
            fontSize: 'var(--text-12)',
            fontFamily: 'var(--font-mono)',
            color: 'var(--gray-500)',
          }}
        >
          <span>
            Showing {(page * pageSize + 1).toLocaleString()}–{Math.min((page + 1) * pageSize, sorted.length).toLocaleString()} of {sorted.length.toLocaleString()}
          </span>
          <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <button
              className="btn btn-ghost btn-icon"
              onClick={() => setPage(p => Math.max(0, p - 1))}
              disabled={page === 0}
              style={{ padding: 4, opacity: page === 0 ? 0.3 : 1 }}
              aria-label="Previous page"
            >
              <ChevronLeft size={14} />
            </button>
            {/* Page number indicators — show max 7 */}
            {Array.from({ length: Math.min(totalPages, 7) }).map((_, i) => {
              let pageNum: number;
              if (totalPages <= 7) {
                pageNum = i;
              } else if (page < 3) {
                pageNum = i;
              } else if (page > totalPages - 4) {
                pageNum = totalPages - 7 + i;
              } else {
                pageNum = page - 3 + i;
              }
              return (
                <button
                  key={pageNum}
                  className="btn btn-ghost"
                  onClick={() => setPage(pageNum)}
                  style={{
                    padding: '2px 8px',
                    fontWeight: pageNum === page ? 700 : 400,
                    color: pageNum === page ? 'var(--accent)' : 'var(--gray-500)',
                    background: pageNum === page ? 'var(--accent-dim)' : 'transparent',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: 11,
                    minWidth: 28,
                  }}
                >
                  {pageNum + 1}
                </button>
              );
            })}
            <button
              className="btn btn-ghost btn-icon"
              onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))}
              disabled={page >= totalPages - 1}
              style={{ padding: 4, opacity: page >= totalPages - 1 ? 0.3 : 1 }}
              aria-label="Next page"
            >
              <ChevronRight size={14} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
