import type { Metadata } from "next";

import { AccountWorkspace } from "@/components/AccountWorkspace";
import { slugToAccountName } from "@/lib/utils";

type AccountPageProps = {
  params: Promise<{ name: string }>;
};

export async function generateMetadata({
  params,
}: AccountPageProps): Promise<Metadata> {
  const { name } = await params;
  const accountName = slugToAccountName(name);

  return {
    title: `${accountName} | QBR Co-Pilot`,
  };
}

export default async function AccountPage({ params }: AccountPageProps) {
  const { name } = await params;
  const accountName = slugToAccountName(name);

  return <AccountWorkspace accountName={accountName} />;
}
