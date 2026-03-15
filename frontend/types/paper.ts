export interface Author {
  name: string;
  authorId?: string;
}

export interface Paper {
  paperId: string;
  title: string;
  year?: number;
  authors: Author[];
  abstract?: string;
  citationCount?: number;
  externalIds?: Record<string, string>;
  url?: string;
}

export interface ResolveResponse {
  paperId: string;
}
