import React from "react";
import {
  flexRender,
  getCoreRowModel,
  useReactTable,
  createColumnHelper
} from "@tanstack/react-table";

type DataRow = {
  region: string;
  datetime: string;
  usage_mw: number;
};

const columnHelper = createColumnHelper<DataRow>();

const columns = [
  columnHelper.accessor("region", {
    header: "Region",
    cell: info => info.getValue()
  }),
  columnHelper.accessor("datetime", {
    header: "Datetime",
    cell: info => info.getValue()
  }),
  columnHelper.accessor("usage_mw", {
    header: "Usage (MW)",
    cell: info => info.getValue()
  })
];

type Props = {
  data: DataRow[];
};

const DataTable: React.FC<Props> = ({ data }) => {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel()
  });

  return (
    <table>
      <thead>
        {table.getHeaderGroups().map(headerGroup => (
          <tr key={headerGroup.id}>
            {headerGroup.headers.map(header => (
              <th key={header.id}>
                {flexRender(header.column.columnDef.header, header.getContext())}
              </th>
            ))}
          </tr>
        ))}
      </thead>
      <tbody>
        {table.getRowModel().rows.map(row => (
          <tr key={row.id}>
            {row.getVisibleCells().map(cell => (
              <td key={cell.id}>
                {flexRender(cell.column.columnDef.cell, cell.getContext())}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default DataTable;
